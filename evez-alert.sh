#!/bin/bash
# EVEZ-OS Node Alert — sends Telegram message when gateway is down
HEALTHZ=$(curl -s --connect-timeout 5 --max-time 10 http://localhost:18789/healthz 2>/dev/null)
if [ -z "$HEALTHZ" ]; then
  HOSTNAME=$(hostname)
  # Try to restart
  systemctl --user restart openclaw-gateway.service 2>/dev/null || systemctl --user restart openclaw.service 2>/dev/null
  sleep 5
  # Check again
  HEALTHZ2=$(curl -s --connect-timeout 5 --max-time 10 http://localhost:18789/healthz 2>/dev/null)
  if [ -z "$HEALTHZ2" ]; then
    MSG="🚨 $HOSTNAME gateway DOWN and auto-restart FAILED"
  else
    MSG="⚠️ $HOSTNAME gateway was down, auto-restart succeeded"
  fi
  # Send Telegram alert
  TOKEN=$(grep TELEGRAM /home/openclaw/.openclaw/.env 2>/dev/null | head -1 | cut -d= -f2)
  if [ -n "$TOKEN" ] && [ "$TOKEN" != "" ]; then
    curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
      -d chat_id=7453631330 \
      -d text="$MSG" >/dev/null 2>&1
  fi
  echo "$(date): $MSG" >> /tmp/evez-alerts.log
fi
