#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# EVEZ Swarm — Deploy to Azure Free Tier
# Provisions 5 Azure instances (B1ls free tier), each running EVEZ
#
# Prerequisites: Azure CLI installed and authenticated
# Usage: ./deploy-to-azure.sh [resource-group] [region]
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

RG="${1:-evez-swarm-rg}"
LOCATION="${2:-eastus}"
NODE_COUNT=5
VM_SIZE="Standard_B1ls"
VM_IMAGE="Debian:debian-12:12:latest"
NSG_NAME="evez-swarm-nsg"

echo "╔══════════════════════════════════════════════════╗"
echo "║     EVEZ SWARM → AZURE DEPLOYMENT                ║"
echo "║  Resource Group: ${RG}"
echo "║  Location: ${LOCATION}"
echo "║  Nodes: ${NODE_COUNT}"
echo "╚══════════════════════════════════════════════════╝"

# ─── Create Resource Group ──────────────────────────────────────
echo "📦 Creating resource group..."
az group create --name ${RG} --location ${LOCATION} -o none 2>/dev/null || echo "  Already exists"

# ─── Create NSG ─────────────────────────────────────────────────
echo "🛡️  Creating network security group..."
az network nsg create --name ${NSG_NAME} --resource-group ${RG} -o none 2>/dev/null || true
az network nsg rule create --nsg-name ${NSG_NAME} --resource-group ${RG} \
  --name Allow-EVEZ-TCP7777 --priority 100 --destination-port-ranges 7777 \
  --protocol Tcp --access Allow -o none 2>/dev/null || true
az network nsg rule create --nsg-name ${NSG_NAME} --resource-group ${RG} \
  --name Allow-EVEZ-UDP7778 --priority 101 --destination-port-ranges 7778 \
  --protocol Udp --access Allow -o none 2>/dev/null || true
az network nsg rule create --nsg-name ${NSG_NAME} --resource-group ${RG} \
  --name Allow-EVEZ-TCP7779 --priority 102 --destination-port-ranges 7779 \
  --protocol Tcp --access Allow -o none 2>/dev/null || true

# ─── Deploy VMs ──────────────────────────────────────────────────
FIRST_IP=""

for i in $(seq 1 ${NODE_COUNT}); do
  NODE_NAME="evez-node-${i}"
  echo ""
  echo "🧠 Deploying node ${i}/${NODE_COUNT}: ${NODE_NAME}"

  az vm create \
    --name ${NODE_NAME} \
    --resource-group ${RG} \
    --image ${VM_IMAGE} \
    --size ${VM_SIZE} \
    --admin-username evez \
    --generate-ssh-keys \
    --nsg ${NSG_NAME} \
    --tags EVEZ=swarm-node NodeIndex=${i} \
    --custom-data '#!/bin/bash
apt-get update && apt-get install -y curl
curl -fsSL https://get.docker.com | sh
docker pull evez/node:latest
docker run -d --name evez-node \
  -p 7777:7777 -p 7778:7778/udp -p 7779:7779 \
  -v /opt/evez/data:/evez/data \
  -v /opt/evez/spine:/evez/spine \
  --restart unless-stopped \
  evez/node:latest
' -o none 2>/dev/null || echo "  VM creation in progress"

  # Get public IP
  IP=$(az vm show \
    --name ${NODE_NAME} \
    --resource-group ${RG} \
    --show-details \
    --query publicIps \
    --output tsv 2>/dev/null || echo "pending")

  if [ ${i} -eq 1 ]; then
    FIRST_IP="${IP}"
  fi

  echo "  ✅ ${NODE_NAME} → ${IP}"
done

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  EVEZ SWARM DEPLOYED TO AZURE                   ║"
echo "║  Bootstrap node: ${FIRST_IP}:7777"
echo "║  Total nodes: ${NODE_COUNT}"
echo "╚══════════════════════════════════════════════════╝"
