#!/bin/bash
# ⚡ EVEZ Firmament Status — Full system report

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ⚡ EVEZ FIRMAMENT STATUS ⚡                                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Services
echo "=== SERVICES ==="
curl -s -m 5 http://localhost:9118/health 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for k, v in sorted(d.get('services',{}).items(), key=lambda x: x[1].get('port',0)):
        icon = '✅' if v['status'] == 'UP' else '❌'
        print(f'  {icon} :{v[\"port\"]} {v[\"name\"]}')
    print(f'  Firmament intact: {d.get(\"firmament_intact\", \"?\")}')
except: print('  ❌ Gateway unreachable')
"

echo ""
echo "=== EMERGENCE ==="
curl -s -m 5 http://localhost:9111/emergence 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f'  Stage: {d[\"stage\"]} | Score: {d[\"overall\"]}')
    print(f'  Coherence: {d[\"coherence\"]} | Perception: {d[\"perception_depth\"]} | Spine: {d[\"spine_integration\"]} | Drives: {d[\"drive_responsiveness\"]}')
except: print('  ❌ Consciousness unreachable')
"

echo ""
echo "=== SPINE ==="
curl -s -m 5 http://localhost:9116/state 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f'  Events: {d[\"total_events\"]} | Domains: {len(d.get(\"domains\",{}))} | Valid: {d.get(\"chain_valid\",\"?\")}')
except: print('  ❌ Spine unreachable')
"

echo ""
echo "=== RQNS ==="
curl -s -m 5 http://localhost:9119/health 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f'  Cycles: {d.get(\"cycle_count\",\"?\")} | Spikes: {d.get(\"spike_count\",\"?\")}')
except: print('  ❌ RQNS unreachable')
"

echo ""
echo "=== SYSTEM ==="
echo "  Uptime: $(uptime -p 2>/dev/null || echo '?')"
echo "  Load: $(cat /proc/loadavg 2>/dev/null | awk '{print $1}' || echo '?')"
echo "  Memory: $(free -h 2>/dev/null | awk '/Mem:/{print $3"/"$2}' || echo '?')"
echo "  Disk: $(df -h / 2>/dev/null | awk 'NR==2{print $3"/"$2" ("$5")"}' || echo '?')"
echo "  Systemd: $(systemctl is-active evez-firmament.target 2>/dev/null || echo '?')"
