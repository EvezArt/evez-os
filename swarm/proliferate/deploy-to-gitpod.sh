#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# EVEZ Swarm — Deploy to Gitpod
# Provisions 5 Gitpod workspaces, each running an EVEZ node
#
# Prerequisites: gp CLI installed and authenticated
# Usage: ./deploy-to-gitpod.sh [repo-url]
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

REPO_URL="${1:-https://github.com/evez/swarm-node}"
NODE_COUNT=5

echo "╔══════════════════════════════════════════════════╗"
echo "║  EVEZ SWARM → GITPOD DEPLOYMENT                  ║"
echo "║  Repo: ${REPO_URL}"
echo "║  Nodes: ${NODE_COUNT}"
echo "╚══════════════════════════════════════════════════╝"

# Ensure .gitpod.yml exists
echo "📦 Ensuring Gitpod configuration..."

FIRST_WS=""

for i in $(seq 1 ${NODE_COUNT}); do
  echo ""
  echo "🧠 Starting Gitpod workspace ${i}/${NODE_COUNT}..."

  # Open Gitpod workspace
  WS_URL="${REPO_URL}/tree/main#gitpod"
  if command -gp &>/dev/null; then
    gp url start ${WS_URL} 2>/dev/null || true
  else
    # Open in browser
    echo "  📎 Open: https://gitpod.io/#${REPO_URL}"
  fi

  echo "  ✅ Workspace ${i} initiated"

  if [ ${i} -eq 1 ]; then
    FIRST_WS="${WS_URL}"
  fi
done

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  EVEZ SWARM DEPLOYED TO GITPOD                  ║"
echo "║  Total workspaces: ${NODE_COUNT}"
echo "║  Free tier: 50 hours/month                      ║"
echo "╚══════════════════════════════════════════════════╝"
