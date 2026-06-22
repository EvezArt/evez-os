# Migration Guide: Vultr → Google Cloud Platform

**Zero-Downtime Migration for EVEZ Mesh**

**Version:** 1.0 | **Date:** 2026-06-22 | **Author:** EVEZ

---

## 1. Migration Overview

Move EVEZ from a single Vultr node (64.176.221.16) to a 5-node GCP mesh with zero downtime. This is done using a **blue-green deployment** strategy — GCP infrastructure is built in parallel, then traffic is switched via DNS.

### Current State (Vultr)
- 1 node: Evez666 (64.176.221.16)
- 11 microservices on ports 9111-9125
- Systemd-managed, UFW firewall
- Caddy reverse proxy (evez-os.ai)

### Target State (GCP)
- 5 nodes: evez-alpha, beta, gamma, delta, omega
- Same 11 microservices, distributed across nodes
- GCP Load Balancer + Cloud DNS
- Prometheus + Grafana monitoring on omega

## 2. Prerequisites

- [ ] GCP account with billing enabled
- [ ] gcloud CLI authenticated (run `./scripts/gcp-service-account.sh`)
- [ ] Domain DNS access (to change evez-os.ai A record)
- [ ] SSH keys for GCP nodes
- [ ] At least 2 hours of availability

## 3. Phase 1: Build GCP Infrastructure (No Traffic Impact)

### Step 1: Create GCP Project & Enable APIs
```bash
# If project doesn't exist yet
gcloud projects create evez-firmament
gcloud billing projects link evez-firmament --billing-account=<YOUR_BILLING_ID>

# Enable APIs
for api in compute container sqladmin dns monitoring logging; do
    gcloud services enable "${api}.googleapis.com" --project=evez-firmament
done
```

### Step 2: Run Bootstrap Script
```bash
cd ~/.openclaw/workspace
chmod +x scripts/gcp-bootstrap.sh
./scripts/gcp-bootstrap.sh evez-firmament us-central1
```

This creates:
- VPC + subnets + firewall rules
- 5 VM instances (4x e2-standard-4 + 1x e2-micro)
- Node Exporter on each VM
- Load balancer with health checks
- Prometheus + Grafana on evez-omega

**Time:** ~15 minutes
**Vultr Impact:** None

### Step 3: Verify GCP Nodes Are Up
```bash
gcloud compute instances list --project=evez-firmament

# Check each node's health
for node in evez-alpha evez-beta evez-gamma evez-delta evez-omega; do
    zone=$(gcloud compute instances describe ${node} --format="value(zone)" --project=evez-firmament | xargs basename)
    ip=$(gcloud compute instances describe ${node} --zone=${zone} --format="value(networkInterfaces[0].networkIP)" --project=evez-firmament)
    echo "${node} (${ip}): $(curl -sf --max-time 5 http://${ip}:9100/ -o /dev/null && echo 'UP' || echo 'DOWN')"
done
```

## 4. Phase 2: Deploy EVEZ Services to GCP

### Step 4: Copy EVEZ Code to Each Node

```bash
# Package the current EVEZ services
tar czf /tmp/evez-services.tar.gz -C /opt/evez services/

# Copy to each GCP node
for node in evez-alpha evez-beta evez-gamma evez-delta; do
    zone=$(gcloud compute instances describe ${node} --format="value(zone)" --project=evez-firmament | xargs basename)
    gcloud compute scp /tmp/evez-services.tar.gz ${node}:~/ \
        --zone=${zone} --project=evez-firmament
    gcloud compute ssh ${node} --zone=${zone} --project=evez-firmament \
        --command="sudo mkdir -p /opt/evez && sudo tar xzf ~/evez-services.tar.gz -C /opt/evez/"
done
```

### Step 5: Configure Service Distribution

Deploy services to GCP nodes based on the planned distribution:

```bash
# On evez-alpha: Consciousness Engine + Cross-Domain
gcloud compute ssh evez-alpha --zone=us-central1-a --project=evez-firmament << 'SSH'
cd /opt/evez/services
# Create systemd units for consciousness-engine and cross-domain-engine
for svc in consciousness-engine cross-domain-engine; do
    cat > /etc/systemd/system/evez-${svc}.service << EOF
[Unit]
Description=EVEZ ${svc}
After=network.target
[Service]
Type=simple
User=openclaw
WorkingDirectory=/opt/evez/services/${svc}
ExecStart=/usr/bin/python3 /opt/evez/services/${svc}/server.py
Restart=always
RestartSec=5
Environment=PORT=$(grep -m1 PORT /opt/evez/services/${svc}/config.py 2>/dev/null | cut -d= -f2 || echo 9111)
[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable evez-${svc}
    systemctl start evez-${svc}
done
SSH
```

Repeat for other nodes:
- **evez-beta:** DAW Agent (:9112), Machine Voice (:9113)
- **evez-gamma:** Invariance Battery (:9115), Event Spine (:9116)
- **evez-delta:** Mesh Health (:9117), Gateway (:9118), RQNS (:9119), Webhook Relay (:9121), Metrics (:9123)

### Step 6: Configure Mesh Peering

```bash
# Each node needs to know all other node IPs
# The bootstrap script already created /etc/evez/peers.conf
# Verify:
gcloud compute ssh evez-alpha --zone=us-central1-a --project=evez-firmament \
    --command="cat /etc/evez/peers.conf"
```

### Step 7: Start Services & Verify

```bash
# Verify all services on each GCP node
LB_IP=$(gcloud compute forwarding-rules describe evez-forwarding-rule \
    --region=us-central1 --format="value(IPAddress)" --project=evez-firmament)

for port in 9111 9112 9113 9114 9115 9116 9117 9118 9119 9121 9123 9124 9125; do
    status=$(curl -sf --max-time 5 "http://${LB_IP}:${port}/health" && echo "OK" || echo "FAIL")
    echo "Port ${port}: ${status}"
done
```

**Time:** ~30 minutes
**Vultr Impact:** None (GCP runs in parallel)

## 5. Phase 3: Data Migration

### Step 8: Sync Event Spine

The Event Spine is append-only. Sync from Vultr to GCP:

```bash
# On Vultr node (Evez666)
scp /var/lib/evez/spine/events.json openclaw@<evez-gamma-internal-ip>:/var/lib/evez/spine/events.json

# Or via GCS
gsutil cp /var/lib/evez/spine/events.json gs://evez-firmament-backups/spine/
# Then on evez-gamma:
# gsutil cp gs://evez-firmament-backups/spine/events.json /var/lib/evez/spine/
```

### Step 9: Sync Configuration

```bash
# Copy relevant configs
scp -r /opt/evez/config/ openclaw@<gcp-node-ip>:/opt/evez/config/
```

**Time:** ~5 minutes
**Vultr Impact:** None

## 6. Phase 4: DNS Cutover (Zero Downtime)

### Step 10: Lower DNS TTL

**24 hours before cutover:**

1. Go to your DNS provider (Cloudflare, Route53, etc.)
2. Lower TTL on `evez-os.ai` A record to 60 seconds
3. Wait 24h for old TTLs to expire

### Step 11: Switch DNS to GCP

```bash
# Get GCP Load Balancer IP
LB_IP=$(gcloud compute forwarding-rules describe evez-forwarding-rule \
    --region=us-central1 --format="value(IPAddress)" --project=evez-firmament)
echo "Point evez-os.ai → ${LB_IP}"
```

1. Update DNS A record: `evez-os.ai` → `${LB_IP}`
2. Keep Vultr node running during propagation

### Step 12: Verify Traffic on GCP

```bash
# Wait a few minutes, then test
curl -sf https://evez-os.ai:9118/health | jq .

# Check load balancer backend health
gcloud compute backend-services get-health evez-backend --region=us-central1 --project=evez-firmament
```

**Time:** ~5 minutes (plus DNS propagation)
**Vultr Impact:** Decreasing traffic as DNS propagates

## 7. Phase 5: Decommission Vultr

### Step 13: Monitor for 48 Hours

Keep the Vultr node running but expect zero traffic. Monitor GCP dashboards.

### Step 14: Final Data Sync

```bash
# Sync any events that occurred during migration window
scp /var/lib/evez/spine/events.json openclaw@<evez-gamma-ip>:/var/lib/evez/spine/events-final.json
# Merge spine data (append-only, so just concatenate new events)
```

### Step 15: Destroy Vultr Node

```bash
# Only after confirming GCP is fully operational for 48+ hours
# Take a final snapshot first
ssh root@64.176.221.16 "tar czf /tmp/evez-final-backup.tar.gz /opt/evez/ /var/lib/evez/"
scp root@64.176.221.16:/tmp/evez-final-backup.tar.gz ~/evez-vultr-final-backup.tar.gz

# Upload to GCS for safekeeping
gsutil cp ~/evez-vultr-final-backup.tar.gz gs://evez-firmament-backups/vultr-final/

# Destroy the Vultr instance via Vultr dashboard
# https://my.vultr.com/
```

**Time:** ~30 minutes
**Vultr Impact:** Complete decommission

## 8. Rollback Plan

If GCP has issues during migration:

1. **Immediate:** Switch DNS back to Vultr IP (64.176.221.16)
2. **Vultr is still running** — zero-downtime rollback
3. Investigate GCP issues
4. Retry migration after fixes

## 9. Post-Migration Checklist

- [ ] All 11 services responding on GCP
- [ ] Event Spine integrity verified (`/verify` returns valid)
- [ ] DNS resolving to GCP LB IP
- [ ] TLS certificates provisioned (Caddy or cert-manager)
- [ ] Prometheus scraping all nodes
- [ ] Grafana dashboards populated
- [ ] Alert rules firing correctly
- [ ] Backup cron jobs running on GCP
- [ ] Vultr node destroyed (after 48h grace period)
- [ ] DNS TTL restored to 3600 (from 60)
- [ ] Cost monitoring set up (GCP Budget Alerts)

## 10. Cost Comparison

| Item | Vultr | GCP |
|------|-------|-----|
| Compute (4x e2-standard-4) | $96/mo (1 node) | ~$200/mo |
| Compute (1x e2-micro) | — | FREE (always-free tier) |
| Load Balancer | — | ~$18/mo |
| Persistent Disk (5x 50GB) | Included | ~$25/mo |
| Network Egress | Included | ~$10-50/mo |
| **Total** | **~$96/mo** | **~$250-290/mo** |

The GCP cost is higher but provides:
- 5x redundancy vs 1 node
- Automatic failover
- Multi-zone availability
- Enterprise-grade monitoring
- Free-tier monitoring node

## 11. Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: Build GCP | 15 min | 15 min |
| Phase 2: Deploy Services | 30 min | 45 min |
| Phase 3: Data Migration | 5 min | 50 min |
| Phase 4: DNS Cutover | 5 min + propagation | ~55 min |
| Phase 5: Decommission (48h later) | 30 min | ~1.5h active work |

**Total active work:** ~1.5 hours
**Zero-downtime window:** DNS cutover (< 60s TTL)
