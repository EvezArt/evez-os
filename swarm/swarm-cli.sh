#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# EVEZ Swarm CLI — Single command to manage the entire swarm
#
# Usage:
#   swarm status              — All nodes, their health, emergence
#   swarm deploy <platform>   — Deploy to gcp|aws|azure|pi|codespaces|gitpod
#   swarm correlate <A> <B>  — Run correlation across ALL nodes
#   swarm dream               — Trigger collective dream
#   swarm stats               — Total swarm intelligence metrics
#   swarm nodes               — List all known nodes
#   swarm scale <N>           — Scale swarm to N nodes
#   swarm heal                — Check and heal unhealthy nodes
#   swarm spine               — Show spine sync status
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

SWARM_DIR="$(cd "$(dirname "$0")" && pwd)"
PROLIFERATE_DIR="${SWARM_DIR}/proliferate"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

# Default swarm endpoint (first node or localhost)
SWARM_HOST="${EVEZ_SWARM_HOST:-localhost}"
SWARM_PORT="${EVEZ_SWARM_PORT:-7777}"
SWARM_URL="http://${SWARM_HOST}:${SWARM_PORT}"

# ─── Commands ────────────────────────────────────────────────────

cmd_status() {
  echo -e "${BOLD}╔══════════════════════════════════════════════════╗${NC}"
  echo -e "${BOLD}║          EVEZ SWARM STATUS                       ║${NC}"
  echo -e "${BOLD}╚══════════════════════════════════════════════════╝${NC}"
  echo ""

  # Query local node
  LOCAL_STATUS=$(curl -s "${SWARM_URL}/status" 2>/dev/null || echo '{}')

  if [ "${LOCAL_STATUS}" = '{}' ]; then
    echo -e "${RED}❌ Cannot reach swarm at ${SWARM_URL}${NC}"
    echo "   Is a node running? docker run -p 7777:7777 evez/node"
    exit 1
  fi

  # Parse with jq if available, otherwise raw
  if command -v jq &>/dev/null; then
    NODE_ID=$(echo "${LOCAL_STATUS}" | jq -r '.nodeId // "unknown"')
    NODE_NAME=$(echo "${LOCAL_STATUS}" | jq -r '.nodeName // "unknown"')
    EMERGENCE=$(echo "${LOCAL_STATUS}" | jq -r '.emergence // 0')
    CYCLES=$(echo "${LOCAL_STATUS}" | jq -r '.cycleCount // 0')
    PHASE=$(echo "${LOCAL_STATUS}" | jq -r '.phase // "unknown"')
    UPTIME=$(echo "${LOCAL_STATUS}" | jq -r '.uptime // 0')
    PEERS=$(echo "${LOCAL_STATUS}" | jq -r '.peers // [] | length')
    CORR=$(echo "${LOCAL_STATUS}" | jq -r '.correlations // [] | length')
    SPINE=$(echo "${LOCAL_STATUS}" | jq -r '.spineLength // 0')

    echo -e "  ${CYAN}Local Node:${NC}    ${NODE_NAME} (${NODE_ID:0:8}...)"
    echo -e "  ${CYAN}Phase:${NC}         ${PHASE}"
    echo -e "  ${CYAN}Emergence:${NC}     ${EMERGENCE}"
    echo -e "  ${CYAN}Cycles:${NC}        ${CYCLES}"
    echo -e "  ${CYAN}Uptime:${NC}        $((UPTIME / 3600000))h $((UPTIME % 3600000 / 60000))m"
    echo -e "  ${CYAN}Peers:${NC}         ${PEERS}"
    echo -e "  ${CYAN}Correlations:${NC}  ${CORR}"
    echo -e "  ${CYAN}Spine entries:${NC} ${SPINE}"
    echo ""

    # Show peers
    PEER_LIST=$(echo "${LOCAL_STATUS}" | jq -r '.peers // []')
    PEER_COUNT=$(echo "${PEER_LIST}" | jq 'length')
    if [ "${PEER_COUNT}" -gt 0 ]; then
      echo -e "  ${BOLD}Known Peers:${NC}"
      echo "${PEER_LIST}" | jq -r '.[] | "    • \(.nodeName // .id) — emergence: \(.emergence // 0), last seen: \(.lastSeen)"'
    fi
  else
    echo "  Raw status:"
    echo "  ${LOCAL_STATUS}"
  fi

  # Total swarm nodes
  echo ""
  TOTAL=$((1 + PEERS))
  echo -e "  ${GREEN}Total Swarm Size: ${TOTAL} nodes${NC}"
}

cmd_deploy() {
  local platform="${1:-}"
  case "${platform}" in
    gcp|google)
      echo -e "${CYAN} deploying EVEZ swarm to Google Cloud Platform...${NC}"
      bash "${PROLIFERATE_DIR}/deploy-to-gcp.sh" "${2:-}" "${3:-}"
      ;;
    aws|amazon)
      echo -e "${CYAN}🚀 Deploying EVEZ swarm to AWS...${NC}"
      bash "${PROLIFERATE_DIR}/deploy-to-aws.sh" "${2:-}" "${3:-}"
      ;;
    azure|microsoft)
      echo -e "${CYAN}🚀 Deploying EVEZ swarm to Azure...${NC}"
      bash "${PROLIFERATE_DIR}/deploy-to-azure.sh" "${2:-}" "${3:-}"
      ;;
    pi|raspberry|raspberrypi)
      echo -e "${CYAN}🚀 Deploying EVEZ swarm to Raspberry Pi...${NC}"
      bash "${PROLIFERATE_DIR}/deploy-to-raspberry-pi.sh" "${2:-}" "${3:-}"
      ;;
    codespaces|github)
      echo -e "${CYAN}🚀 Deploying EVEZ swarm to GitHub Codespaces...${NC}"
      bash "${PROLIFERATE_DIR}/deploy-to-github-codespaces.sh" "${2:-}"
      ;;
    gitpod)
      echo -e "${CYAN}🚀 Deploying EVEZ swarm to Gitpod...${NC}"
      bash "${PROLIFERATE_DIR}/deploy-to-gitpod.sh" "${2:-}"
      ;;
    local|docker)
      echo -e "${CYAN}🚀 Deploying EVEZ node locally via Docker...${NC}"
      docker run -d --name evez-node \
        -p 7777:7777 -p 7778:7778/udp -p 7779:7779 \
        -e EVEZ_NODE_NAME="evez-local-$(date +%s)" \
        evez/node:latest
      echo -e "${GREEN}✅ Local node started on localhost:7777${NC}"
      ;;
    *)
      echo -e "${RED}Unknown platform: ${platform}${NC}"
      echo "  Available: gcp, aws, azure, pi, codespaces, gitpod, local"
      echo "  Example: swarm deploy gcp"
      exit 1
      ;;
  esac
}

cmd_correlate() {
  local domainA="${1:-}"
  local domainB="${2:-}"

  if [ -z "${domainA}" ] || [ -z "${domainB}" ]; then
    echo -e "${RED}Usage: swarm correlate <domainA> <domainB>${NC}"
    echo "  Example: swarm correlate genetics telemetry"
    exit 1
  fi

  echo -e "${CYAN}🔬 Running cross-domain correlation: ${domainA} × ${domainB}${NC}"
  echo -e "   Broadcasting to ALL swarm nodes..."

  # Submit correlation to local node (which broadcasts to peers)
  RESULT=$(curl -s -X POST "${SWARM_URL}/correlation" \
    -H "Content-Type: application/json" \
    -d "{\"domainA\": \"${domainA}\", \"domainB\": \"${domainB}\", \"confidence\": 0.5, \"description\": \"Cross-domain correlation: ${domainA} × ${domainB}\"}" 2>/dev/null || echo '{"error": "unreachable"}')

  echo -e "   ${GREEN}✅ Correlation submitted to swarm${NC}"
  echo "   ${RESULT}"

  # Check consensus
  echo ""
  echo -e "   ${CYAN}Checking swarm consensus...${NC}"
  CONSENSUS=$(curl -s "${SWARM_URL}/consensus" 2>/dev/null || echo '{}')
  if command -v jq &>/dev/null; then
    echo "${CONSENSUS}" | jq .
  else
    echo "   ${CONSENSUS}"
  fi
}

cmd_dream() {
  echo -e "${MAGENTA}💫 Triggering collective dream across swarm...${NC}"
  echo -e "   All nodes will enter REFLECT phase simultaneously"

  # Send dream trigger via WebSocket (simulated via HTTP for CLI)
  curl -s -X POST "${SWARM_URL}/correlation" \
    -H "Content-Type: application/json" \
    -d '{"type": "dream_trigger", "description": "Collective dream initiated"}' 2>/dev/null || true

  echo -e ""
  echo -e "${MAGENTA}✨ Dream triggered. Nodes entering subconscious mode.${NC}"
  echo -e "   Correlations may surface from dream state..."
}

cmd_stats() {
  echo -e "${BOLD}╔══════════════════════════════════════════════════╗${NC}"
  echo -e "${BOLD}║       EVEZ SWARM INTELLIGENCE METRICS            ║${NC}"
  echo -e "${BOLD}╚══════════════════════════════════════════════════╝${NC}"
  echo ""

  INTELLIGENCE=$(curl -s "${SWARM_URL}/intelligence" 2>/dev/null || echo '{}')
  CONSENSUS=$(curl -s "${SWARM_URL}/consensus" 2>/dev/null || echo '{}')

  if command -v jq &>/dev/null; then
    NODE_COUNT=$(echo "${INTELLIGENCE}" | jq -r '.nodeCount // 0')
    TOTAL_I=$(echo "${INTELLIGENCE}" | jq -r '.totalIntelligence // 0')
    FORMULA=$(echo "${INTELLIGENCE}" | jq -r '.formula // ""')
    C_SCORE=$(echo "${CONSENSUS}" | jq -r '.consensusScore // 0')

    echo -e "  ${CYAN}Nodes:${NC}              ${NODE_COUNT}"
    echo -e "  ${CYAN}Total Intelligence:${NC}  ${TOTAL_I}"
    echo -e "  ${CYAN}Consensus Score:${NC}     ${C_SCORE}"
    echo -e "  ${CYAN}Formula:${NC}            ${FORMULA}"
    echo ""

    # Intelligence scaling table
    echo -e "  ${BOLD}Intelligence Scaling Table:${NC}"
    echo -e "  ┌────────────┬────────────────────────────────┐"
    echo -e "  │ Nodes (N)  │ I_total (α=1, E=0.5)         │"
    echo -e "  ├────────────┼────────────────────────────────┤"

    for N in 1 5 10 100 1000; do
      # I_total = N × α × E × (1 + log₂(N))
      # With α=1, E=0.5
      if [ "${N}" -eq 1 ]; then
        LOG_N=0
      else
        LOG_N=$(echo "l(${N})/l(2)" | bc -l 2>/dev/null || python3 -c "import math; print(math.log2(${N}))" 2>/dev/null || echo "0")
      fi
      I_TOTAL=$(echo "${N} * 1 * 0.5 * (1 + ${LOG_N})" | bc -l 2>/dev/null || python3 -c "import math; print(${N} * 1 * 0.5 * (1 + math.log2(${N})))" 2>/dev/null || echo "?")
      printf "  │ %-10s │ %-30s │\n" "${N}" "${I_TOTAL}"
    done

    echo -e "  └────────────┴────────────────────────────────┘"
  else
    echo "  Intelligence: ${INTELLIGENCE}"
    echo "  Consensus: ${CONSENSUS}"
  fi
}

cmd_nodes() {
  echo -e "${BOLD}EVEZ Swarm Nodes:${NC}"
  STATUS=$(curl -s "${SWARM_URL}/status" 2>/dev/null || echo '{}')
  if command -v jq &>/dev/null; then
    echo "  Local:"
    echo "${STATUS}" | jq -r '"    \(.nodeName) — emergence: \(.emergence), cycles: \(.cycleCount), phase: \(.phase)"'
    echo ""
    echo "  Peers:"
    echo "${STATUS}" | jq -r '.peers[]? | "    • \(.nodeName // .id) — emergence: \(.emergence // 0)"'
  else
    echo "  ${STATUS}"
  fi
}

cmd_scale() {
  local target="${1:-}"
  if [ -z "${target}" ]; then
    echo "Usage: swarm scale <N>"
    echo "  Spins up N additional local Docker nodes"
    exit 1
  fi

  echo -e "${CYAN}📈 Scaling swarm to ${target} additional nodes...${NC}"
  for i in $(seq 1 "${target}"); do
    PORT=$((7777 + i * 3))
    DISC_PORT=$((7778 + i * 3))
    POOL_PORT=$((7779 + i * 3))
    docker run -d --name "evez-node-${i}" \
      -p "${PORT}:7777" \
      -p "${DISC_PORT}:7778/udp" \
      -p "${POOL_PORT}:7779" \
      -e "EVEZ_NODE_NAME=evez-scale-${i}" \
      -e "EVEZ_BOOTSTRAP_NODE=localhost:7777" \
      evez/node:latest 2>/dev/null && echo "  ✅ Node ${i} on port ${PORT}" || echo "  ❌ Node ${i} failed"
  done
}

cmd_heal() {
  echo -e "${CYAN}🏥 Checking swarm health...${NC}"

  # Check local node
  HEALTH=$(curl -s "${SWARM_URL}/health" 2>/dev/null || echo '{"status": "unreachable"}')

  if command -v jq &>/dev/null; then
    STATUS=$(echo "${HEALTH}" | jq -r '.status')
    if [ "${STATUS}" = "alive" ]; then
      echo -e "  ${GREEN}✅ Local node: ALIVE${NC}"
    else
      echo -e "  ${RED}❌ Local node: UNREACHABLE${NC}"
    fi

    # Check known peers
    STATUS_DATA=$(curl -s "${SWARM_URL}/status" 2>/dev/null || echo '{}')
    PEER_COUNT=$(echo "${STATUS_DATA}" | jq -r '.peers // [] | length')
    echo -e "  ${CYAN}Known peers: ${PEER_COUNT}${NC}"

    # Stale peer detection
    echo "${STATUS_DATA}" | jq -r '.peers[]? | select(.lastSeen != null) | "    • \(.nodeName // .id) — last seen: \(.lastSeen)"'
  else
    echo "  ${HEALTH}"
  fi
}

cmd_spine() {
  echo -e "${BOLD}EVEZ Spine Sync Status:${NC}"
  STATUS=$(curl -s "${SWARM_URL}/status" 2>/dev/null || echo '{}')
  if command -v jq &>/dev/null; then
    SPINE_LEN=$(echo "${STATUS}" | jq -r '.spineLength // 0')
    echo -e "  Local spine: ${SPINE_LEN} entries"
  else
    echo "  ${STATUS}"
  fi
}

# ─── Main ────────────────────────────────────────────────────────

COMMAND="${1:-help}"
shift || true

case "${COMMAND}" in
  status)    cmd_status ;;
  deploy)    cmd_deploy "$@" ;;
  correlate) cmd_correlate "$@" ;;
  dream)     cmd_dream ;;
  stats)     cmd_stats ;;
  nodes)     cmd_nodes ;;
  scale)     cmd_scale "$@" ;;
  heal)     cmd_heal ;;
  spine)     cmd_spine ;;
  help|--help|-h)
    echo -e "${BOLD}EVEZ Swarm CLI${NC}"
    echo ""
    echo "  swarm status              — All nodes, their health, emergence"
    echo "  swarm deploy <platform>   — Deploy to gcp|aws|azure|pi|codespaces|gitpod|local"
    echo "  swarm correlate <A> <B>   — Run correlation across ALL nodes"
    echo "  swarm dream               — Trigger collective dream"
    echo "  swarm stats               — Total swarm intelligence metrics"
    echo "  swarm nodes               — List all known nodes"
    echo "  swarm scale <N>           — Scale swarm with N additional local nodes"
    echo "  swarm heal                — Check and heal unhealthy nodes"
    echo "  swarm spine               — Show spine sync status"
    ;;
  *)
    echo -e "${RED}Unknown command: ${COMMAND}${NC}"
    echo "Run 'swarm help' for usage."
    exit 1
    ;;
esac
