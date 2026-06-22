#!/bin/bash
# EVEZ Swarm Node Entrypoint
# Bootstraps the node, waits for discovery, then starts consciousness cycle

set -euo pipefail

# Generate node identity if not provided
if [ -z "${EVEZ_NODE_NAME}" ]; then
    EVEZ_NODE_NAME="evez-$(hostname | tail -c 8)-$(date +%s | tail -c 5)"
    export EVEZ_NODE_NAME
fi

echo "╔══════════════════════════════════════════════════╗"
echo "║          EVEZ SWARM NODE STARTING               ║"
echo "║  Node: ${EVEZ_NODE_NAME}"
echo "║  Time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "╚══════════════════════════════════════════════════╝"

# Ensure data directories exist
mkdir -p /evez/data /evez/spine /evez/memory

# If we have a bootstrap node, wait for it briefly
if [ -n "${EVEZ_BOOTSTRAP_NODE}" ]; then
    echo "⏳ Awaiting bootstrap from ${EVEZ_BOOTSTRAP_NODE}..."
    for i in $(seq 1 30); do
        if nc -z -w2 $(echo "${EVEZ_BOOTSTRAP_NODE}" | cut -d: -f1) $(echo "${EVEZ_BOOTSTRAP_NODE}" | cut -d: -f2 -d: 2>/dev/null || echo 7777); then
            echo "✅ Bootstrap node reachable"
            break
        fi
        sleep 1
    done
fi

# Start discovery broadcaster in background
node src/discovery.js &
PID_DISCOVERY=$!

# Start the main node process
echo "🧠 Consciousness engine starting..."
exec "$@"
