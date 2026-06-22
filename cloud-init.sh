#!/bin/bash
# ============================================================================
# cloud-init.sh — EVEZ Mesh GCP Instance Provisioning
#
# Run as a GCP startup-script or cloud-init user-data.
# Provisions a fresh Debian/Ubuntu GCP instance with all 11 EVEZ services
# running as systemd services via Docker Compose.
#
# Usage:
#   1. As GCP startup-script metadata:
#      gcloud compute instances create evez-mesh \
#        --metadata-from-file startup-script=cloud-init.sh
#
#   2. As cloud-init user-data:
#      gcloud compute instances create evez-mesh \
#        --metadata=user-data="$(cat cloud-init.sh)"
#
#   3. Directly on an existing instance:
#      bash cloud-init.sh
# ============================================================================

set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────────────────

EVEZ_USER="${EVEZ_USER:-evez}"
EVEZ_HOME="/home/${EVEZ_USER}"
EVEZ_REPO="${EVEZ_REPO:-https://github.com/EvezArt/evez-os.git}"
EVEZ_BRANCH="${EVEZ_BRANCH:-main}"
NODE_NAME="${EVEZ_NODE_NAME:-Evez666}"
NODE_IP="${EVEZ_NODE_IP:-}"

LOGFILE="/var/log/evez-cloud-init.log"

# Redirect all output to log
exec > >(tee -a "$LOGFILE") 2>&1

echo "═══════════════════════════════════════════════════════════"
echo "  EVEZ Mesh — Cloud-Init Provisioning"
echo "  Started: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "═══════════════════════════════════════════════════════════"

# ─── 1. System Update & Base Packages ────────────────────────────────────────

echo ">>> [1/10] System update & base packages..."
apt-get update -y
apt-get upgrade -y
apt-get install -y \
    curl wget git jq unzip net-tools \
    apt-transport-https ca-certificates \
    gnupg lsb-release software-properties-common \
    iptables-persistent htop nano

# ─── 2. Create EVEZ User ────────────────────────────────────────────────────

echo ">>> [2/10] Creating EVEZ user..."
if ! id "$EVEZ_USER" &>/dev/null; then
    useradd -m -s /bin/bash "$EVEZ_USER"
    echo "$EVEZ_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/evez
fi

# ─── 3. Install Docker ──────────────────────────────────────────────────────

echo ">>> [3/10] Installing Docker..."
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | bash
    usermod -aG docker "$EVEZ_USER"
    systemctl enable docker
    systemctl start docker
fi
echo "  Docker: $(docker --version)"

# ─── 4. Install Docker Compose V2 ──────────────────────────────────────────

echo ">>> [4/10] Installing Docker Compose..."
if ! docker compose version &>/dev/null; then
    mkdir -p /usr/local/lib/docker/cli-plugins
    COMPOSE_VERSION="2.32.4"
    curl -fsSL \
        "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-linux-x86_64" \
        -o /usr/local/lib/docker/cli-plugins/docker-compose
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
fi
echo "  Compose: $(docker compose version)"

# ─── 5. Install Node.js 22 ─────────────────────────────────────────────────

echo ">>> [5/10] Installing Node.js 22..."
if ! command -v node &>/dev/null || [[ "$(node --version)" != v22* ]]; then
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
    apt-get install -y nodejs
fi
echo "  Node: $(node --version)"

# ─── 6. Install OpenClaw ───────────────────────────────────────────────────

echo ">>> [6/10] Installing OpenClaw..."
if ! command -v openclaw &>/dev/null; then
    npm install -g openclaw@latest
fi
echo "  OpenClaw: $(openclaw --version 2>/dev/null || echo 'installed')"

# ─── 7. Clone EVEZ Repository ──────────────────────────────────────────────

echo ">>> [7/10] Cloning EVEZ repository..."
WORKSPACE="${EVEZ_HOME}/.openclaw/workspace"
if [ ! -d "${WORKSPACE}/.git" ]; then
    mkdir -p "$(dirname "$WORKSPACE")"
    git clone -b "$EVEZ_BRANCH" "$EVEZ_REPO" "$WORKSPACE" 2>&1 || echo "  Clone may have failed, continuing..."
    chown -R "$EVEZ_USER:$EVEZ_USER" "$WORKSPACE"
fi

# ─── 8. Configure Firewall ─────────────────────────────────────────────────

echo ">>> [8/10] Configuring firewall..."

# EVEZ service ports
for port in 9111 9112 9113 9114 9115 9116 9117 9118 9119 9121 9123 9124 9125; do
    iptables -A INPUT -p tcp --dport "$port" -j ACCEPT 2>/dev/null || true
done

# SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT 2>/dev/null || true

# Docker ports
iptables -A INPUT -i docker0 -j ACCEPT 2>/dev/null || true

# Save rules
netfilter-persistent save 2>/dev/null || iptables-save > /etc/iptables/rules.v4 2>/dev/null || true

# ─── 9. Start EVEZ Services ─────────────────────────────────────────────────

echo ">>> [9/10] Starting EVEZ services via Docker Compose..."

# Auto-detect public IP if not set
if [ -z "$NODE_IP" ]; then
    NODE_IP=$(curl -s --max-time 5 http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google" 2>/dev/null || curl -s --max-time 5 ifconfig.me 2>/dev/null || echo "127.0.0.1")
fi

cd "$WORKSPACE"

# Deploy with docker compose
sudo -u "$EVEZ_USER" -E \
    EVEZ_NODE_NAME="$NODE_NAME" \
    EVEZ_NODE_IP="$NODE_IP" \
    docker compose up -d 2>&1 || {
        echo "  Docker Compose failed, falling back to direct Python services..."
        # Fallback: run services directly
        for svc in event_spine consciousness_engine daw_agent machine_voice cross_domain invariance mesh_health gateway rqns webhook_relay metrics; do
            if [ -f "src/services/${svc}.py" ]; then
                nohup python3 "src/services/${svc}.py" > "/tmp/evez-${svc}.log" 2>&1 &
                echo "  Started ${svc} (PID $!)"
            fi
        done
    }

# ─── 10. Create Systemd Service for OpenClaw Gateway ────────────────────────

echo ">>> [10/10] Configuring systemd services..."

# OpenClaw Gateway service
cat > /etc/systemd/system/openclaw-gateway.service << 'EOF'
[Unit]
Description=OpenClaw Gateway
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=simple
User=evez
WorkingDirectory=/home/evez/.openclaw/workspace
ExecStart=/usr/bin/openclaw gateway start
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable openclaw-gateway 2>/dev/null || true
systemctl start openclaw-gateway 2>/dev/null || true

# EVEZ health watchdog
cat > /etc/systemd/system/evez-watchdog.service << 'EOF'
[Unit]
Description=EVEZ Mesh Health Watchdog
After=docker.service
Wants=docker.service

[Service]
Type=simple
User=evez
WorkingDirectory=/home/evez/.openclaw/workspace
ExecStart=/bin/bash scripts/mesh-watchdog.sh
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable evez-watchdog 2>/dev/null || true
systemctl start evez-watchdog 2>/dev/null || true

# ─── Completion ──────────────────────────────────────────────────────────────

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ EVEZ Mesh — Cloud-Init Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  Node:     $NODE_NAME"
echo "  IP:       $NODE_IP"
echo "  Services:  9111-9117 (mesh), 9118 (gateway), 9119 (rqns)"
echo "            9121 (webhooks), 9123 (metrics), 9124 (geo), 9125 (tts)"
echo "  Compose:  cd $WORKSPACE && docker compose ps"
echo "  Logs:     docker compose logs -f"
echo "  Health:   curl http://$NODE_IP:9118/health"
echo ""

# Signal ready
echo "EVEZ MESH READY — $(date -u '+%Y-%m-%dT%H:%M:%SZ')" > /tmp/evez-ready
