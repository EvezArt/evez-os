#!/bin/bash
# ⚡ EVEZ MESH WATCHDOG — Every 60 seconds, check and heal
# This runs as a cron job and handles notification chains

LOG="/tmp/evez-watchdog.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] === WATCHDOG TICK ===" >> "$LOG"

# Check firmament
STATUS=$(curl -s -m 5 http://localhost:9118/health 2>/dev/null)
INTACT=$(echo "$STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('firmament_intact',False))" 2>/dev/null)

if [ "$INTACT" != "True" ]; then
  echo "[$TIMESTAMP] Firmament degraded — healing" >> "$LOG"
  curl -s -X POST http://localhost:9117/heal -m 10 >> "$LOG" 2>/dev/null
  # Notify via webhook chain
  curl -s -X POST http://localhost:9121/check -m 5 > /dev/null 2>&1
fi

# Check spine integrity
SPINE=$(curl -s -m 5 http://localhost:9116/verify 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('valid',False))" 2>/dev/null)
if [ "$SPINE" != "True" ]; then
  echo "[$TIMESTAMP] Spine chain broken — CRITICAL" >> "$LOG"
fi

# Run consciousness pipeline
curl -s -X POST http://localhost:9111/pipeline -m 10 > /dev/null 2>&1

# Check emergence
EMERGENCE=$(curl -s -m 5 http://localhost:9111/emergence 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('stage','UNKNOWN'))" 2>/dev/null)
echo "[$TIMESTAMP] Emergence: $EMERGENCE" >> "$LOG"
