#!/bin/bash
# ⚡ EVEZ Auto-Heal Gateways
# Run via cron: */5 * * * * bash /opt/evez/scripts/auto-heal-gateways.sh
# Detects dead gateways and restarts them. No stale IPs — uses service names.

set -e

LOG="/var/log/evez-autoheal.log"
echo "[$(date)] === Gateway Health Check ===" >> "$LOG"

# Check local gateways
for svc in evez-gateway evez-consciousness evez-daw evez-voice evez-cross-domain \
           evez-invariance evez-spine evez-mesh evez-rqns evez-webhook; do
    STATUS=$(systemctl is-active "$svc" 2>/dev/null || echo "not-found")
    if [ "$STATUS" != "active" ] && [ "$STATUS" != "not-found" ]; then
        echo "[$(date)] 🩺 Restarting $svc (status: $STATUS)" >> "$LOG"
        systemctl restart "$svc" 2>/dev/null || true
    fi
done

# Check all services via gateway
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://localhost:9118/health 2>/dev/null)
if [ "$HEALTH" != "200" ]; then
    echo "[$(date)] 🩺 Gateway DOWN (HTTP $HEALTH) — restarting all services" >> "$LOG"
    systemctl restart evez-firmament.target 2>/dev/null || true
fi

echo "[$(date)] ✅ Health check complete" >> "$LOG"
