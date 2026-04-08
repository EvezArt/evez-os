#!/bin/bash
# Simple EVEZ Health & Sync Loop
# Run this in background with: nohup ./simple_maintenance.sh &

LOG="/var/log/evez-maintenance.log"
WORKSPACE="/root/.openclaw/workspace"

echo "[$(date)] EVEZ Maintenance starting..." >> "$LOG"

cd "$WORKSPACE"

while true; do
    echo "[$(date)] Health check" >> "$LOG"
    /usr/local/bin/openclaw status --short >> "$LOG" 2>&1 || echo "[$(date)] OpenClaw check done" >> "$LOG"
    
    echo "[$(date)] Git sync check" >> "$LOG"
    git add -A 2>/dev/null
    git diff --quiet --cached || git commit -m "Auto sync $(date +%Y-%m-%d-%H:%M)" 2>/dev/null
    git push origin twin-autonomy 2>/dev/null || echo "[$(date)] Git push skipped (no changes)" >> "$LOG"
    
    echo "[$(date)] Cycle complete, sleeping 5 min..." >> "$LOG"
    sleep 300
done
