#!/bin/bash
# EVEZ Cognition Spree Cross-Node Sync
# Syncs encrypted cognition sprees from all 5 GCP nodes to gcp-west (central store)
# Runs every 30 minutes via cron

CENTRAL_NODE="gcp-west"
STORE_DIR="$HOME/.openclaw/cognition-store"
REMOTE_DIR="/home/openclaw/.openclaw/cognition-store"

mkdir -p "$STORE_DIR"

for host in gcp-small gcp-power gcp-openclaw gcp-knot; do
  # Sync encrypted spree files from each node
  rsync -az --timeout=30 \
    "$host:$REMOTE_DIR/sprees-*.enc.jsonl" \
    "$STORE_DIR/from-$host/" 2>/dev/null
  
  # Sync SQLite index
  rsync -az --timeout=30 \
    "$host:$REMOTE_DIR/index.db" \
    "$STORE_DIR/from-$host/index.db" 2>/dev/null
done

# Merge all sprees into central store
for dir in "$STORE_DIR"/from-*/; do
  if [ -d "$dir" ]; then
    for f in "$dir"sprees-*.enc.jsonl; do
      if [ -f "$f" ]; then
        node=$(basename "$dir" | sed 's/from-//')
        # Append to central with node prefix to avoid collision
        cp "$f" "$STORE_DIR/sprees-merged-$(basename $f .enc.jsonl)-$node.enc.jsonl" 2>/dev/null
      fi
    done
  fi
done

# Log sync
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "$TS spree-sync complete" >> "$STORE_DIR/sync.log"
