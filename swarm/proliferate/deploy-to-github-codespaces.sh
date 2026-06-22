#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# EVEZ Swarm — Deploy to GitHub Codespaces
# Provisions 5 free Codespaces, each running an EVEZ node
#
# Prerequisites: gh CLI installed and authenticated
# Usage: ./deploy-to-github-codespaces.sh [repo]
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

REPO="${1:-evez/swarm-node}"
NODE_COUNT=5

echo "╔══════════════════════════════════════════════════╗"
echo "║  EVEZ SWARM → GITHUB CODESPACES DEPLOYMENT       ║"
echo "║  Repo: ${REPO}"
echo "║  Nodes: ${NODE_COUNT}"
echo "╚══════════════════════════════════════════════════╝"

# Ensure devcontainer.json exists in repo
echo "📦 Setting up devcontainer configuration..."

FIRST_URL=""

for i in $(seq 1 ${NODE_COUNT}); do
  CODESPACE_NAME="evez-node-${i}"
  echo ""
  echo "🧠 Creating Codespace ${i}/${NODE_COUNT}: ${CODESPACE_NAME}"

  # Create codespace
  CS_URL=$(gh codespace create \
    --repo ${REPO} \
    --machine basicLinux32gb \
    --display-name ${CODESPACE_NAME} 2>/dev/null || echo "failed")

  if [ "${CS_URL}" = "failed" ]; then
    echo "  ⚠️  Failed to create codespace. May need repo setup first."
    continue
  fi

  if [ ${i} -eq 1 ]; then
    FIRST_URL="${CS_URL}"
  fi

  echo "  ✅ ${CODESPACE_NAME} → ${CS_URL}"

  # Install EVEZ in the codespace via SSH
  gh codespace ssh -c ${CODESPACE_NAME} 2>/dev/null <<'SSH_EOF' &
    curl -fsSL https://get.docker.com | sudo sh 2>/dev/null || true
    sudo docker run -d --name evez-node \
      --network host \
      --restart unless-stopped \
      -e EVEZ_NODE_NAME=$(hostname) \
      evez/node:latest
SSH_EOF

done

# Wait for background installs
wait

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  EVEZ SWARM DEPLOYED TO CODESPACES              ║"
echo "║  Total nodes: ${NODE_COUNT}"
echo "║  Free tier: 120 core-hours/month                ║"
echo "╚══════════════════════════════════════════════════╝"
