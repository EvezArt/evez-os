#!/bin/bash
# evez-mesh-health.sh — GCP mutual health check (GCP nodes only)
# Runs every 60 seconds. Checks GCP siblings. Logs only. NO auto-restart.

# Auto-detect self by checking local IPs against the list
GCP_NODES=(
  "34.53.51.34:evez-primary"
  "136.118.144.227:openclaw-gcp"
  "136.113.102.152:openclaw-power-node"
  "35.222.248.151:evez-gcp-openclaw"
  "34.23.192.213:evez-free-node"
)

HEALTH_LOG="$HOME/.openclaw/workspace/mesh-health.log"
mkdir -p "$(dirname "$HEALTH_LOG")"

for ENTRY in "${GCP_NODES[@]}"; do
  IP="${ENTRY%%:*}"
  NAME="${ENTRY#*:}"
  
  # Skip self
  if hostname -I 2>/dev/null | grep -q "$IP"; then
    continue
  fi
  
  STATUS=$(curl -sf --connect-timeout 3 "http://$IP:18789/healthz" 2>/dev/null || echo "DOWN")
  
  if [ "$STATUS" = "DOWN" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] WARN: $NAME ($IP) is DOWN" >> "$HEALTH_LOG"
    # NO auto-restart. Just log. Vultr-KNOT handles recovery via its own sentinel.
  else
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] OK: $NAME ($IP) is LIVE" >> "$HEALTH_LOG"
  fi
done

# Keep only last 500 lines
if [ -f "$HEALTH_LOG" ] && [ $(wc -l < "$HEALTH_LOG") -gt 500 ]; then
  tail -500 "$HEALTH_LOG" > "$HEALTH_LOG.tmp" && mv "$HEALTH_LOG.tmp" "$HEALTH_LOG"
fi
