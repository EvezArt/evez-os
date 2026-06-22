#!/bin/bash
# ⚡ FIRMAMENT START — Launch all 8 EVEZ microservices
SERVICES=(consciousness_engine daw_agent machine_voice cross_domain invariance event_spine mesh_health gateway)
DIR="/home/openclaw/.openclaw/workspace/src/services"

for svc in "${SERVICES[@]}"; do
  if ! curl -s http://localhost:0/health >/dev/null 2>&1; then
    # Check if already running by checking the port
    PORT=$(grep -oP 'port.*?(\d+)' "$DIR/${svc}.py" 2>/dev/null | head -1 | grep -oP '\d+')
    if [ -n "$PORT" ] && curl -s "http://localhost:$PORT/health" >/dev/null 2>&1; then
      echo "✅ $svc already running on :$PORT"
    else
      nohup python3 "$DIR/${svc}.py" > "/tmp/evez-${svc}.log" 2>&1 &
      echo "🚀 $svc launched"
    fi
  fi
done

sleep 2
echo ""
echo "=== FIRMAMENT STATUS ==="
for port in 9111 9112 9113 9114 9115 9116 9117 9118; do
  if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
    echo "✅ :$port UP"
  else
    echo "❌ :$port DOWN"
  fi
done
