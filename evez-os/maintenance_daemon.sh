#!/bin/bash
# EVEZ OS Background Maintenance Daemon
# Runs continuously, executing tasks at intervals

LOG_FILE="/var/log/evez-maintenance.log"
WORKSPACE="/root/.openclaw/workspace"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M')] $1" | tee -a "$LOG_FILE"
}

# Daemon loop
log "EVEZ Maintenance Daemon starting..."

while true; do
    # Health check (every 15 min = 900s)
    log "Health check..."
    /usr/local/bin/openclaw status --short >> "$LOG_FILE" 2>&1 || log "Health check failed"
    
    # Git sync (every 60 min = 3600s)
    # Check if last commit was more than 50 minutes ago
    cd "$WORKSPACE"
    LAST_COMMIT=$(git log -1 --format=%cd --date=format:'%Y-%m-%d %H:%M' 2>/dev/null)
    log "Last commit: $LAST_COMMIT"
    
    # Context bridge sync (every 30 min = 1800s)
    log "Context bridge sync..."
    if [ -f evez-os/core/context/stm.json ]; then
        size=$(stat -c%s evez-os/core/context/stm.json 2>/dev/null || echo 0)
        log "STM size: $size bytes"
    fi
    
    # Sleep 60 seconds between cycles
    log "Sleeping 60s..."
    sleep 60
done
