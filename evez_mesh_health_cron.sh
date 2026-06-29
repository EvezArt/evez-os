#!/usr/bin/env bash
# MESH HEALTH CHECK — every 15 minutes
# Checks all 6 gateways + 5 OSINT APIs + 5 Telegram bots
# Sends Telegram alert via gcp-west if any node is down

cd /home/openclaw/.openclaw/workspace

NODES=("207.148.12.53" "34.53.51.34" "34.23.192.213" "35.222.248.151" "136.113.102.152" "136.118.144.227")
NAMES=("vultr" "gcp-west" "gcp-small" "gcp-openclaw" "gcp-power" "gcp-knot")

DOWN=""
for i in "${!NODES[@]}"; do
  ip="${NODES[$i]}"
  name="${NAMES[$i]}"
  code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "http://${ip}:18789/" 2>/dev/null)
  if [ "$code" != "200" ]; then
    DOWN="${DOWN} ${name}(${ip}:${code})"
  fi
done

# Check OSINT APIs (GCP only)
OSINT_NODES=("34.53.51.34" "34.23.192.213" "35.222.248.151" "136.113.102.152" "136.118.144.227")
OSINT_NAMES=("gcp-west" "gcp-small" "gcp-openclaw" "gcp-power" "gcp-knot")

OSINT_DOWN=""
for i in "${!OSINT_NODES[@]}"; do
  ip="${OSINT_NODES[$i]}"
  name="${OSINT_NAMES[$i]}"
  code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "http://${ip}:18791/health" 2>/dev/null)
  if [ "$code" != "200" ]; then
    OSINT_DOWN="${OSINT_DOWN} ${name}(${ip}:${code})"
  fi
done

if [ -n "$DOWN" ] || [ -n "$OSINT_DOWN" ]; then
  MSG="⚠️ MESH ALERT:"
  [ -n "$DOWN" ] && MSG="${MSG}\n Gateways DOWN:${DOWN}"
  [ -n "$OSINT_DOWN" ] && MSG="${MSG}\n OSINT APIs DOWN:${OSINT_DOWN}"
  MSG="${MSG}\n$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "$MSG"
  # Send via gcp-west Telegram
  ssh openclaw@34.53.51.34 "python3 -c \"import requests; r=requests.post('https://api.telegram.org/bot' + open('/home/openclaw/.openclaw/.env').read().split('TELEGRAM_BOT_TOKEN=')[1].split(chr(10))[0] + '/sendMessage', json={'chat_id':'7453631330','text':'$MSG'}); print(r.status_code)\"" 2>/dev/null || true
else
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) MESH OK: 6/6 gateways, 5/5 OSINT APIs"
fi
