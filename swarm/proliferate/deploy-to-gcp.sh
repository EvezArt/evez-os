#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# EVEZ Swarm — Deploy to Google Cloud Platform
# Provisions 5 GCP instances, each running an EVEZ swarm node
#
# Prerequisites: gcloud CLI installed and authenticated
# Usage: ./deploy-to-gcp.sh [project-id] [region]
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null || echo 'evez-swarm')}"
REGION="${2:-us-central1}"
ZONE="${REGION}-a"
MACHINE_TYPE="e2-micro"
NODE_COUNT=5
IMAGE_FAMILY="debian-12"
IMAGE_PROJECT="debian-cloud"
NETWORK="evez-swarm-net"
FIREWALL_RULE="evez-swarm-allow-swarm"

echo "╔══════════════════════════════════════════════════╗"
echo "║     EVEZ SWARM → GCP DEPLOYMENT                  ║"
echo "║  Project: ${PROJECT_ID}"
echo "║  Region:  ${REGION}"
echo "║  Nodes:   ${NODE_COUNT}"
echo "╚══════════════════════════════════════════════════╝"

# ─── Create VPC Network ──────────────────────────────────────────
echo "🌐 Creating VPC network..."
gcloud compute networks create ${NETWORK} \
  --project=${PROJECT_ID} \
  --subnet-mode=auto 2>/dev/null || echo "  Network already exists"

echo "🔥 Creating firewall rules..."
gcloud compute firewall-rules create ${FIREWALL_RULE} \
  --network=${NETWORK} \
  --allow=tcp:7777,tcp:7779,udp:7778 \
  --source-ranges=0.0.0.0/0 \
  --description="EVEZ swarm ports" 2>/dev/null || echo "  Firewall rule already exists"

# ─── Deploy Nodes ────────────────────────────────────────────────
FIRST_IP=""

for i in $(seq 1 ${NODE_COUNT}); do
  NODE_NAME="evez-node-${i}"
  echo ""
  echo "🧠 Deploying node ${i}/${NODE_COUNT}: ${NODE_NAME}"

  # Create instance
  gcloud compute instances create ${NODE_NAME} \
    --project=${PROJECT_ID} \
    --zone=${ZONE} \
    --machine-type=${MACHINE_TYPE} \
    --image-family=${IMAGE_FAMILY} \
    --image-project=${IMAGE_PROJECT} \
    --network=${NETWORK} \
    --tags=evez-swarm \
    --metadata=startup-script='#!/bin/bash
apt-get update && apt-get install -y curl
curl -fsSL https://get.docker.com | sh
usermod -aG docker $(whoami)
docker pull evez/node:latest
docker run -d --name evez-node \
  -p 7777:7777 -p 7778:7778/udp -p 7779:7779 \
  -v /opt/evez/data:/evez/data \
  -v /opt/evez/spine:/evez/spine \
  -e EVEZ_NODE_NAME='${NODE_NAME}' \
  --restart unless-stopped \
  evez/node:latest
' 2>/dev/null || echo "  Instance already exists"

  # Get IP
  IP=$(gcloud compute instances describe ${NODE_NAME} \
    --zone=${ZONE} \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)' \
    --project=${PROJECT_ID} 2>/dev/null || echo "pending")

  if [ ${i} -eq 1 ]; then
    FIRST_IP="${IP}"
  fi

  echo "  ✅ ${NODE_NAME} → ${IP}"
done

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  EVEZ SWARM DEPLOYED TO GCP                     ║"
echo "║  Bootstrap node: ${FIRST_IP}:7777"
echo "║  Dashboard: http://${FIRST_IP}:7777/status"
echo "║  Total nodes: ${NODE_COUNT}"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "To connect additional nodes, set EVEZ_BOOTSTRAP_NODE=${FIRST_IP}:7777"
