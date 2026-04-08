#!/bin/bash
# EVEZ OS — Auto Maintenance Script
# Run manually or set up via external cron
# Usage: ./auto_maintenance.sh [task]

set -e

WORKSPACE="/root/.openclaw/workspace"
cd "$WORKSPACE"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M')] $1"
}

case "$1" in
    git-sync)
        log "Git sync starting..."
        git add -A
        git commit -m "Auto sync $(date '+%Y-%m-%d-%H:%M')"
        git push origin twin-autonomy
        log "Git sync complete"
        ;;
    health)
        log "OpenClaw health check..."
        /usr/local/bin/openclaw status --short 2>&1 | tail -20
        ;;
    context-bridge)
        log "Context bridge sync..."
        # Read STM, merge to LTM
        if [ -f evez-os/core/context/stm.json ]; then
            log "STM exists, checking size..."
            size=$(stat -f%z evez-os/core/context/stm.json 2>/dev/null || stat -c%s evez-os/core/context/stm.json)
            log "STM size: $size bytes"
        fi
        log "Context bridge complete"
        ;;
    memory-cleanup)
        log "Memory cleanup..."
        find memory/ -name "*.md" -mtime +30 -exec rm -v {} \; 2>/dev/null || true
        log "Memory cleanup complete"
        ;;
    monitor-evez666)
        log "EVEZ666 post monitor..."
        # Placeholder for X API integration
        log "EVEZ666 monitor complete"
        ;;
    all)
        log "Running all maintenance tasks..."
        $0 git-sync
        $0 health
        $0 context-bridge
        $0 memory-cleanup
        log "All maintenance complete"
        ;;
    *)
        echo "EVEZ OS Auto Maintenance"
        echo "Usage: $0 [task]"
        echo ""
        echo "Tasks:"
        echo "  git-sync        - Git add, commit, push"
        echo "  health          - OpenClaw health check"
        echo "  context-bridge  - Sync STM to LTM"
        echo "  memory-cleanup  - Remove old memory files"
        echo "  monitor-evez666 - Monitor EVEZ666 posts"
        echo "  all             - Run all tasks"
        ;;
esac
