#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# EVEZ Swarm — Deploy to Raspberry Pi (Local Hardware)
# Installs EVEZ node on each Pi via SSH
#
# Prerequisites: SSH access to each Pi, Docker installed
# Usage: ./deploy-to-raspberry-pi.sh [pi1,pi2,pi3,...]
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

PI_LIST="${1:-}"
PI_USER="${2:-pi}"
SSH_KEY="${3:-~/.ssh/id_rsa}"

# Auto-detect Pis on local network if not specified
if [ -z "${PI_LIST}" ]; then
  echo "🔍 Auto-detecting Raspberry Pis on local network..."
  echo "   (Scanning for hosts responding on port 22 with hostname containing 'raspberry' or 'pi')"
  echo ""
  echo "   If auto-detection fails, provide IPs manually:"
  echo "   ./deploy-to-raspberry-pi.sh '192.168.1.10,192.168.1.11,192.168.1.12'"
  echo ""

  # Try to find Pis via ARP scan
  if command -v arp-scan &>/dev/null; then
    PI_LIST=$(arp-scan --localnet 2>/dev/null | grep -i 'raspberry\|b8:27:eb\|dc:a6:32' | awk '{print $1}' | tr '\n' ',' | sed 's/,$//')
  fi

  if [ -z "${PI_LIST}" ]; then
    echo "⚠️  No Pis auto-detected. Provide IPs as argument."
    echo "   Example: ./deploy-to-raspberry-pi.sh '10.0.0.5,10.0.0.6'"
    exit 1
  fi
fi

# Parse into array
IFS=',' read -ra PI_ADDRS <<< "${PI_LIST}"
NODE_COUNT=${#PI_ADDRS[@]}

echo "╔══════════════════════════════════════════════════╗"
echo "║     EVEZ SWARM → RASPBERRY PI DEPLOYMENT         ║"
echo "║  Pis: ${NODE_COUNT}"
echo "║  User: ${PI_USER}"
echo "║  Addresses: ${PI_LIST}"
echo "╚══════════════════════════════════════════════════╝"

# Build ARM64 image locally if needed
echo ""
echo "🏗️  Building EVEZ node image for ARM64..."
if command -v docker &>/dev/null; then
  docker buildx build --platform linux/arm64 \
    -t evez/node:arm64 \
    -f /home/openclaw/.openclaw/workspace/swarm/node/Dockerfile \
    /home/openclaw/.openclaw/workspace/swarm/node/ 2>/dev/null || {
    echo "⚠️  Docker buildx not available. Will install from source on each Pi."
  }
fi

FIRST_IP=""

for i in "${!PI_ADDRS[@]}"; do
  PI_IP="${PI_ADDRS[$i]}"
  NODE_NAME="evez-pi-$((i+1))"
  echo ""
  echo "🧠 Deploying to Pi ${i+1}/${NODE_COUNT}: ${PI_IP}"

  if [ ${i} -eq 0 ]; then
    FIRST_IP="${PI_IP}"
  fi

  BOOTSTRAP_FLAG=""
  if [ -n "${FIRST_IP}" ] && [ "${PI_IP}" != "${FIRST_IP}" ]; then
    BOOTSTRAP_FLAG="-e EVEZ_BOOTSTRAP_NODE=${FIRST_IP}:7777"
  fi

  ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${PI_USER}@${PI_IP} <<DEPLOY_EOF
    set -e
    echo "  📦 Installing Docker..."
    curl -fsSL https://get.docker.com | sudo sh 2>/dev/null || true
    sudo usermod -aG docker ${PI_USER}

    echo "  📥 Pulling EVEZ node image..."
    sudo docker pull evez/node:latest 2>/dev/null || {
      echo "  🔨 Building from source..."
      sudo apt-get update && sudo apt-get install -y git nodejs npm
      git clone https://github.com/evez/swarm-node /tmp/evez-node 2>/dev/null || true
      cd /tmp/evez-node && sudo docker build -t evez/node .
    }

    echo "  🚀 Starting EVEZ node..."
    sudo docker rm -f evez-node 2>/dev/null || true
    sudo docker run -d --name evez-node \
      --network host \
      --restart unless-stopped \
      -v /opt/evez/data:/evez/data \
      -v /opt/evez/spine:/evez/spine \
      -e EVEZ_NODE_NAME=${NODE_NAME} \
      ${BOOTSTRAP_FLAG} \
      evez/node:latest

    echo "  ✅ ${NODE_NAME} running on ${PI_IP}"
DEPLOY_EOF

done

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  EVEZ SWARM DEPLOYED TO RASPBERRY PI            ║"
echo "║  Bootstrap node: ${FIRST_IP}:7777"
echo "║  Total Pis: ${NODE_COUNT}"
echo "║  Memory: Each Pi adds ~2GB RAM to swarm pool    ║"
echo "╚══════════════════════════════════════════════════╝"
