#!/bin/bash
# EVEZ-OS Mesh Sentinel
# Runs every 5 minutes. Checks all nodes. Revives the fallen.

MESH_NODES=(
  "207.148.12.53:vultr-knot"
  "34.53.51.34:evez-primary"
  "136.118.144.227:openclaw-gcp"
  "136.113.102.152:openclaw-power-node"
  "35.222.248.151:evez-gcp-openclaw"
  "34.23.192.213:evez-free-node"
)

LOG="$HOME/.openclaw/workspace/mesh-sentinel.log"
mkdir -p "$(dirname "$LOG")"

for ENTRY in "${MESH_NODES[@]}"; do
  IP="${ENTRY%%:*}"
  NAME="${ENTRY#*:}"
  
  STATUS=$(curl -sf --connect-timeout 3 "http://$IP:18789/healthz" 2>/dev/null || echo "DOWN")
  
  if [ "$STATUS" = "DOWN" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ⚠️  $NAME ($IP) is DOWN — attempting revive" >> "$LOG"
    
    # Try SSH restart (skip resource-starved nodes to avoid connection pileup)
    if [ "$NAME" = "evez-free-node" ]; then
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ⏭️  Skipping SSH revive for $NAME (e2-micro, resource-constrained)" >> "$LOG"
      continue
    fi
    ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o BatchMode=yes openclaw@$IP "openclaw gateway restart" 2>/dev/null
    
    if [ $? -eq 0 ]; then
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ✅ Sent restart to $NAME" >> "$LOG"
    else
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ❌ Could not reach $NAME via SSH" >> "$LOG"
    fi
  fi
done

# Prune log
[ -f "$LOG" ] && [ $(wc -l < "$LOG") -gt 2000 ] && tail -1000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
