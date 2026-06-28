#!/bin/bash
# evez-meme-pipeline.sh — Auto-meme generator for EVEZ-OS mesh events
# Reads mesh health logs and generates memes based on detected patterns
# Part of the Metarom → VCL → EVEZ-OS narrative meme media pipeline

MEME=/usr/lib/node_modules/openclaw/skills/meme-maker/scripts/meme.mjs
SHARP=/tmp/node_modules/sharp
OUTDIR=/home/openclaw/.openclaw/workspace/memes
mkdir -p "$OUTDIR"

TIMESTAMP=$(date -u +%Y%m%d-%H%M%S)

# Detect events from mesh health log
HEALTH_LOG="/home/openclaw/.openclaw/workspace/mesh-health.log"
NODES_DOWN=0
if [ -f "$HEALTH_LOG" ]; then
  NODES_DOWN=$(grep -c "DOWN" "$HEALTH_LOG" 2>/dev/null || echo 0)
fi

# Pattern: Node goes down → Disaster Girl meme
if [ "$NODES_DOWN" -gt 0 ]; then
  node $MEME render disaster-girl \
    --text "$NODES_DOWN mesh node(s) reporting DOWN" \
    --text "Steven Crawford-Maggard's sentinel" \
    --out "$OUTDIR/disaster-${TIMESTAMP}.svg" 2>/dev/null
  echo "Generated: disaster meme ($NODES_DOWN nodes down)"
fi

# Pattern: Gateway restart detected in journal
RESTARTS=$(journalctl --user -u openclaw-gateway.service --no-pager --since "10 min ago" 2>/dev/null | grep -c "SIGTERM" || echo 0)
if [ "$RESTARTS" -gt 2 ]; then
  node $MEME render this-is-fine \
    --text "Gateway restarted $RESTARTS times in the last 10 minutes" \
    --text "This is fine" \
    --out "$OUTDIR/fine-${TIMESTAMP}.svg" 2>/dev/null
  echo "Generated: this-is-fine meme ($RESTARTS restarts)"
fi

# Pattern: OOM killer active
OOM=$(dmesg 2>/dev/null | grep -c "oom-killer" || echo 0)
if [ "$OOM" -gt 0 ]; then
  node $MEME render buff-doge-cheems \
    --text "Before OOM killer" \
    --text "Steven's RAM budget" \
    --text "After OOM killer" \
    --text "Also Steven's RAM budget" \
    --out "$OUTDIR/oom-${TIMESTAMP}.svg" 2>/dev/null
  echo "Generated: OOM meme"
fi

# Pattern: Sentinel hammering a node
SENTINEL_HITS=$(ps aux | grep -c "ssh.*gateway restart" 2>/dev/null || echo 0)
if [ "$SENTINEL_HITS" -gt 1 ]; then
  node $MEME render expanding-brain \
    --text "Restart the gateway manually" \
    --text "Write a cron to check every minute" \
    --text "Have 3 nodes SSH restart simultaneously" \
    --text "Restart loop caused by the restart loop caused by the restart loop" \
    --out "$OUTDIR/sentinel-${TIMESTAMP}.svg" 2>/dev/null
  echo "Generated: sentinel meme ($SENTINEL_HITS SSH restarts active)"
fi

# Always generate a status summary meme
LIVE=$(grep -c "LIVE\|ok" "$HEALTH_LOG" 2>/dev/null || echo 0)
node $MEME render bernie-asking \
  --text "I am once again asking for all 6 mesh nodes to stay up for more than 5 minutes" \
  --out "$OUTDIR/bernie-${TIMESTAMP}.svg" 2>/dev/null

# Convert SVGs to PNGs
for svg in "$OUTDIR"/*.svg; do
  png="${svg%.svg}.png"
  if [ ! -f "$png" ]; then
    node -e "
      const sharp = require('$SHARP');
      sharp('$svg').png().toFile('$png').then(()=>console.log('Converted: $png')).catch(()=>{});
    " 2>/dev/null
  fi
done

echo "Meme pipeline complete. Output: $OUTDIR"
