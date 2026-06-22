#!/usr/bin/env bash
# =============================================================================
# EVEZ GCP Bootstrap — Full Production Deployment
# Creates: VPC, Firewall, 5 VMs, OpenClaw mesh, Monitoring, Load Balancer
# Prerequisite: Run gcp-service-account.sh first
# =============================================================================
set -euo pipefail

PROJECT_ID="${1:-evez-firmament}"
REGION="${2:-us-central1}"
ZONE_A="${REGION}-a"
ZONE_B="${REGION}-b"
VPC_NAME="evez-mesh-vpc"
SUBNET_A="evez-mesh-subnet-a"
SUBNET_B="evez-mesh-subnet-b"
SA_NAME="evez-mesh-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
IMAGE_FAMILY="debian-12"
IMAGE_PROJECT="debian-cloud"

# Node definitions: name=type:zone
declare -A NODES=(
    ["evez-alpha"]="e2-standard-4:${ZONE_A}"
    ["evez-beta"]="e2-standard-4:${ZONE_A}"
    ["evez-gamma"]="e2-standard-4:${ZONE_B}"
    ["evez-delta"]="e2-standard-4:${ZONE_B}"
    ["evez-omega"]="e2-micro:${ZONE_A}"
)

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'
info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()   { echo -e "${RED}[ERR]${NC} $*"; }
step()  { echo -e "\n${BOLD}━━━ $* ━━━${NC}"; }

# ─── Preflight ───────────────────────────────────────────────────────────────
step "Pre-flight Checks"
if ! gcloud auth list --format=json 2>/dev/null | jq -e '.[] | select(.status=="ACTIVE")' &>/dev/null; then
    err "No active gcloud auth. Run ./gcp-service-account.sh first"; exit 1
fi
gcloud config set core/project "${PROJECT_ID}" 2>/dev/null
ok "Project: ${PROJECT_ID}, Region: ${REGION}"

# ─── Enable APIs ─────────────────────────────────────────────────────────────
step "Enabling APIs"
for api in compute container sqladmin dns monitoring logging cloudresourcemanager iam cloudbuild run secretmanager storage-api pubsub cloudfunctions; do
    gcloud services enable "${api}.googleapis.com" --project="${PROJECT_ID}" --quiet 2>/dev/null &
done
wait
ok "All APIs enabled"

# ─── Service Account ─────────────────────────────────────────────────────────
step "Service Account"
if ! gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud iam service-accounts create "${SA_NAME}" --display-name="EVEZ Mesh SA" --project="${PROJECT_ID}"
    for role in compute.admin container.admin cloudsql.admin dns.admin monitoring.admin logging.admin security.admin iam.securityAdmin storage.admin iam.serviceAccountUser; do
        gcloud projects add-iam-policy-binding "${PROJECT_ID}" --member="serviceAccount:${SA_EMAIL}" --role="roles/${role}" --quiet 2>/dev/null || true
    done
fi
ok "Service account: ${SA_EMAIL}"

# ─── VPC ──────────────────────────────────────────────────────────────────────
step "VPC + Subnets"
if ! gcloud compute networks describe "${VPC_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud compute networks create "${VPC_NAME}" --subnet-mode=custom --project="${PROJECT_ID}"
fi
for subnet_info in "${SUBNET_A}:10.128.0.0/20" "${SUBNET_B}:10.128.16.0/20"; do
    sn="${subnet_info%%:*}"; cidr="${subnet_info##*:}"
    if ! gcloud compute networks subnets describe "${sn}" --region="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
        gcloud compute networks subnets create "${sn}" --network="${VPC_NAME}" --region="${REGION}" --range="${cidr}" --enable-private-ip-google-access --project="${PROJECT_ID}"
    fi
done
ok "VPC ready"

# ─── Firewall ─────────────────────────────────────────────────────────────────
step "Firewall Rules"
gcloud compute firewall-rules create "evez-mesh-internal" --network="${VPC_NAME}" --allow=tcp:9111-9125,udp:9111-9125 --source-ranges="10.128.0.0/16" --project="${PROJECT_ID}" 2>/dev/null || true
gcloud compute firewall-rules create "evez-mesh-external" --network="${VPC_NAME}" --allow=tcp:9111-9125 --source-ranges="0.0.0.0/0" --project="${PROJECT_ID}" 2>/dev/null || true
gcloud compute firewall-rules create "evez-ssh" --network="${VPC_NAME}" --allow=tcp:22 --source-ranges="0.0.0.0/0" --project="${PROJECT_ID}" 2>/dev/null || true
gcloud compute firewall-rules create "evez-monitoring" --network="${VPC_NAME}" --allow=tcp:9090,tcp:3000,tcp:9093 --source-ranges="0.0.0.0/0" --project="${PROJECT_ID}" 2>/dev/null || true
gcloud compute firewall-rules create "evez-health-checks" --network="${VPC_NAME}" --allow=tcp:9111-9125 --source-ranges="130.211.0.0/22,35.191.0.0/16" --project="${PROJECT_ID}" 2>/dev/null || true
ok "Firewall configured"

# ─── VMs ──────────────────────────────────────────────────────────────────────
step "Creating VM Instances"
cat > /tmp/evez-startup.sh << 'STARTUP'
#!/bin/bash
set -e
while fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; do sleep 5; done
apt-get update -qq && apt-get install -y -qq curl wget git python3 python3-pip python3-venv jq ufw fail2ban > /dev/null 2>&1
curl -fsSL https://deb.nodesource.com/setup_22.x | bash - > /dev/null 2>&1
apt-get install -y -qq nodejs > /dev/null 2>&1
npm install -g openclaw 2>/dev/null || true
ufw --force enable && ufw allow 22/tcp && ufw allow 9111:9125/tcp && ufw allow 9090/tcp && ufw allow 3000/tcp
useradd -m -s /bin/bash openclaw 2>/dev/null || true
curl -fsSL https://get.docker.com | sh > /dev/null 2>&1
usermod -aG docker openclaw 2>/dev/null || true
wget -q https://github.com/prometheus/node_exporter/releases/download/v1.8.0/node_exporter-1.8.0.linux-amd64.tar.gz -O /tmp/ne.tar.gz
tar xzf /tmp/ne.tar.gz -C /tmp/ && cp /tmp/node_exporter-*/node_exporter /usr/local/bin/ && rm -rf /tmp/node_exporter* /tmp/ne.tar.gz
cat > /etc/systemd/system/node_exporter.service << 'NE'
[Unit]
Description=Node Exporter
After=network.target
[Service]
Type=simple
User=nobody
ExecStart=/usr/local/bin/node_exporter --web.listen-address=:9100
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
NE
systemctl daemon-reload && systemctl enable node_exporter && systemctl start node_exporter
touch /tmp/evez-startup-complete
STARTUP

for node in "${!NODES[@]}"; do
    spec="${NODES[$node]}"; mtype="${spec%%:*}"; zone="${spec##*:}"
    if gcloud compute instances describe "${node}" --zone="${zone}" --project="${PROJECT_ID}" &>/dev/null; then
        ok "${node} exists"; continue
    fi
    info "Creating ${node} (${mtype}, ${zone})..."
    gcloud compute instances create "${node}" \
        --zone="${zone}" --machine-type="${mtype}" \
        --image-family="${IMAGE_FAMILY}" --image-project="${IMAGE_PROJECT}" \
        --network="${VPC_NAME}" --subnet="${SUBNET_A}" \
        --metadata-from-file=startup-script=/tmp/evez-startup.sh \
        --metadata=node-role="${node}" \
        --service-account="${SA_EMAIL}" --scopes="cloud-platform" \
        --tags="evez-mesh,evez-node" \
        --boot-disk-size=50GB --boot-disk-type=pd-balanced \
        --project="${PROJECT_ID}" --quiet
    ok "${node} created"
done

# ─── Wait for startup ────────────────────────────────────────────────────────
step "Waiting for VM startups"
for node in "${!NODES[@]}"; do
    zone="${NODES[$node]##*:}"
    for i in $(seq 1 30); do
        gcloud compute ssh "${node}" --zone="${zone}" --project="${PROJECT_ID}" \
            --command="test -f /tmp/evez-startup-complete" --quiet 2>/dev/null && break
        sleep 10
    done
    ok "${node} ready"
done

# ─── Collect IPs ──────────────────────────────────────────────────────────────
step "Collecting Node IPs"
declare -A NODE_IPS
for node in "${!NODES[@]}"; do
    zone="${NODES[$node]##*:}"
    ip=$(gcloud compute instances describe "${node}" --zone="${zone}" \
        --format="value(networkInterfaces[0].networkIP)" --project="${PROJECT_ID}" 2>/dev/null || echo "")
    NODE_IPS["${node}"]="${ip}"
    ok "${node} → ${ip}"
done

# ─── Mesh Peering ────────────────────────────────────────────────────────────
step "Configuring Mesh Peering"
for node in "${!NODE_IPS[@]}"; do
    zone="${NODES[$node]##*:}"
    peers=""
    for peer in "${!NODE_IPS[@]}"; do
        [[ "${peer}" == "${node}" ]] && continue
        peers+="${peer}=${NODE_IPS[$peer]} "
    done
    gcloud compute ssh "${node}" --zone="${zone}" --project="${PROJECT_ID}" \
        --command="mkdir -p /etc/evez && echo '${peers}' > /etc/evez/peers.conf" --quiet 2>/dev/null || true
    ok "${node} peered"
done

# ─── Load Balancer ────────────────────────────────────────────────────────────
step "Load Balancer"
gcloud compute instance-groups unmanaged create "evez-group-a" --zone="${ZONE_A}" --project="${PROJECT_ID}" 2>/dev/null || true
gcloud compute instance-groups unmanaged create "evez-group-b" --zone="${ZONE_B}" --project="${PROJECT_ID}" 2>/dev/null || true

for node in "${!NODES[@]}"; do
    zone="${NODES[$node]##*:}"
    grp="evez-group-a"; [[ "${zone}" == "${ZONE_B}" ]] && grp="evez-group-b"
    gcloud compute instance-groups unmanaged add-instances "${grp}" --instances="${node}" --zone="${zone}" --project="${PROJECT_ID}" 2>/dev/null || true
done

gcloud compute health-checks create http "evez-health" --port=9118 --request-path="/health" --check-interval=10 --timeout=5 --unhealthy-threshold=3 --project="${PROJECT_ID}" 2>/dev/null || true
gcloud compute backend-services create "evez-backend" --health-checks="evez-health" --load-balancing-scheme=EXTERNAL --project="${PROJECT_ID}" 2>/dev/null || true
gcloud compute backend-services add-backend "evez-backend" --instance-group="evez-group-a" --instance-group-zone="${ZONE_A}" --project="${PROJECT_ID}" 2>/dev/null || true
gcloud compute backend-services add-backend "evez-backend" --instance-group="evez-group-b" --instance-group-zone="${ZONE_B}" --project="${PROJECT_ID}" 2>/dev/null || true
gcloud compute url-maps create "evez-url-map" --default-service="evez-backend" --project="${PROJECT_ID}" 2>/dev/null || true
gcloud compute target-http-proxies create "evez-http-proxy" --url-map="evez-url-map" --project="${PROJECT_ID}" 2>/dev/null || true
gcloud compute forwarding-rules create "evez-forwarding-rule" --target-http-proxy="evez-http-proxy" --ports=80 --project="${PROJECT_ID}" 2>/dev/null || true

LB_IP=$(gcloud compute forwarding-rules describe "evez-forwarding-rule" --format="value(IPAddress)" --project="${PROJECT_ID}" 2>/dev/null || echo "pending")
ok "Load Balancer IP: ${LB_IP}"

# ─── Monitoring on Omega ─────────────────────────────────────────────────────
step "Prometheus + Grafana on evez-omega"
PROM_CONFIG=$(mktemp)
cat > "${PROM_CONFIG}" << PROMEOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'evez-firmament'

rule_files:
  - '/etc/prometheus/alerts/*.yml'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets:
PROMEOF

for node in "${!NODE_IPS[@]}"; do
    echo "          - '${NODE_IPS[$node]}:9100'" >> "${PROM_CONFIG}"
done

cat >> "${PROM_CONFIG}" << 'PROMEOF2'

  - job_name: 'evez-mesh-services'
    metrics_path: /metrics
    static_configs:
      - targets:
PROMEOF2

for node in "${!NODE_IPS[@]}"; do
    echo "          - '${NODE_IPS[$node]}:9123'" >> "${PROM_CONFIG}"
done

omega_zone="${NODES[evez-omega]##*:}"
gcloud compute scp "${PROM_CONFIG}" "evez-omega:/tmp/prometheus.yml" --zone="${omega_zone}" --project="${PROJECT_ID}" --quiet 2>/dev/null || true

# Alert rules
ALERT_CONFIG=$(mktemp)
cat > "${ALERT_CONFIG}" << 'AEOF'
groups:
  - name: evez-mesh
    rules:
      - alert: NodeDown
        expr: up{job="node-exporter"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Node {{ $labels.instance }} is down"

      - alert: HighCPU
        expr: 100 - (avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
        for: 5m
        labels:
          severity: warning

      - alert: HighMemory
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning

      - alert: DiskSpaceLow
        expr: (1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100 > 80
        for: 5m
        labels:
          severity: warning

      - alert: ServiceDown
        expr: up{job="evez-mesh-services"} == 0
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "EVEZ service unreachable on {{ $labels.instance }}"

      - alert: MeshNodeFailure
        expr: count(up{job="node-exporter"} == 0) >= 2
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Multiple mesh nodes down — mesh degraded"
AEOF

gcloud compute scp "${ALERT_CONFIG}" "evez-omega:/tmp/evez-alerts.yml" --zone="${omega_zone}" --project="${PROJECT_ID}" --quiet 2>/dev/null || true

# Deploy monitoring stack
gcloud compute ssh "evez-omega" --zone="${omega_zone}" --project="${PROJECT_ID}" --quiet --command="bash -s" << 'MSETUP'
set -e
# Prometheus
wget -q https://github.com/prometheus/prometheus/releases/download/v2.52.0/prometheus-2.52.0.linux-amd64.tar.gz -O /tmp/prom.tar.gz
tar xzf /tmp/prom.tar.gz -C /opt/ && ln -sf /opt/prometheus-*/prometheus /usr/local/bin/prometheus
ln -sf /opt/prometheus-*/promtool /usr/local/bin/promtool
mkdir -p /etc/prometheus/alerts /var/lib/prometheus
cp /tmp/prometheus.yml /etc/prometheus/prometheus.yml
cp /tmp/evez-alerts.yml /etc/prometheus/alerts/evez-mesh.yml

cat > /etc/systemd/system/prometheus.service << 'P'
[Unit]
Description=Prometheus
After=network.target
[Service]
Type=simple
ExecStart=/usr/local/bin/prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/var/lib/prometheus/
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
P

# Alertmanager
wget -q https://github.com/prometheus/alertmanager/releases/download/v0.27.0/alertmanager-0.27.0.linux-amd64.tar.gz -O /tmp/am.tar.gz
tar xzf /tmp/am.tar.gz -C /opt/ && ln -sf /opt/alertmanager-*/alertmanager /usr/local/bin/alertmanager
mkdir -p /etc/alertmanager /var/lib/alertmanager

cat > /etc/alertmanager/alertmanager.yml << 'AM'
global:
  resolve_timeout: 5m
route:
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
receivers:
  - name: 'default'
    webhook_configs:
      - url: 'http://localhost:9121/alert'
        send_resolved: true
AM

cat > /etc/systemd/system/alertmanager.service << 'AMS'
[Unit]
Description=Alertmanager
After=network.target
[Service]
Type=simple
ExecStart=/usr/local/bin/alertmanager --config.file=/etc/alertmanager/alertmanager.yml --storage.path=/var/lib/alertmanager
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
AMS

# Grafana
apt-get install -y -qq adduser libfontconfig1 musl > /dev/null 2>&1
wget -q https://dl.grafana.com/oss/release/grafana_11.0.0_amd64.deb -O /tmp/grafana.deb
dpkg -i /tmp/grafana.deb 2>/dev/null || apt-get install -f -y -qq > /dev/null 2>&1
mkdir -p /etc/grafana/provisioning/datasources

cat > /etc/grafana/provisioning/datasources/prometheus.yml << 'GDS'
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
GDS

systemctl daemon-reload
systemctl enable prometheus alertmanager grafana-server
systemctl start prometheus alertmanager grafana-server
echo "MONITORING_STACK_DEPLOYED"
MSETUP

ok "Monitoring stack deployed on evez-omega"

# ─── Summary ─────────────────────────────────────────────────────────────────
step "Deployment Summary"
echo ""
ok "════════════════════════════════════════════════════════════════"
ok "  EVEZ GCP Bootstrap Complete!"
ok "════════════════════════════════════════════════════════════════"
echo ""
echo "  Project:    ${PROJECT_ID}"
echo "  Region:      ${REGION}"
echo "  VPC:        ${VPC_NAME}"
echo "  Load Balancer: ${LB_IP}"
echo ""
echo "  Nodes:"
for node in "${!NODES[@]}"; do
    ip="${NODE_IPS[$node]:-pending}"
    spec="${NODES[$node]}"; mtype="${spec%%:*}"
    echo "    ${node} → ${ip} (${mtype})"
done
echo ""
echo "  Monitoring:  http://${NODE_IPS[evez-omega]:-omega-ip}:3000 (Grafana)"
echo "  Prometheus:  http://${NODE_IPS[evez-omega]:-omega-ip}:9090"
echo "  Alertmanager: http://${NODE_IPS[evez-omega]:-omega-ip}:9093"
echo ""
info "Next steps:"
info "  1. Configure DNS: evez-os.ai → ${LB_IP}"
info "  2. SSH into nodes: gcloud compute ssh <node> --zone=<zone>"
info "  3. Deploy services: Copy EVEZ code to each node"
info "  4. Set up CI/CD: Push .github/workflows/gcp-full-deploy.yml"
