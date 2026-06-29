#!/usr/bin/env python3
"""Monitor gateway health - check memory, event loop, disk, sessions."""
import json, subprocess, re, time
from pathlib import Path

ck = {}

# Gateway memory
try:
    import psutil
    for p in psutil.process_iter(['pid', 'name', 'memory_info']):
        if 'openclaw' in (p.info.get('name', '') or ''):
            ck['gw_rss_mb'] = round(p.info['memory_info'].rss / 1048576, 1)
            break
except:
    pass

# Event loop stats
try:
    r = subprocess.run(['openclaw', 'status', '--deep'], capture_output=True, text=True, timeout=15)
    for l in r.stdout.splitlines():
        if 'max' in l and 'p99' in l:
            m = re.search(r'max (\d+)ms.*p99 (\d+)ms.*util ([\d.]+)', l)
            if m:
                ck['ev_max_ms'] = int(m.group(1))
                ck['ev_p99_ms'] = int(m.group(2))
                ck['ev_util'] = float(m.group(3))
except:
    pass

# Disk
try:
    import psutil
    u = psutil.disk_usage('/')
    ck['disk_pct'] = u.percent
    ck['disk_free_gb'] = round(u.free / 1073741824, 1)
except:
    pass

# Sessions size
sf = Path.home() / '.openclaw' / 'agents' / 'main' / 'sessions' / 'sessions.json'
if sf.exists():
    ck['sess_mb'] = round(sf.stat().st_size / 1048576, 2)

# MEMORY.md size
mf = Path('/home/openclaw/.openclaw/workspace/MEMORY.md')
if mf.exists():
    ck['memory_kb'] = round(mf.stat().st_size / 1024, 1)

# Alerts
alerts = []
if ck.get('gw_rss_mb', 0) > 800:
    alerts.append(f"HIGH MEM: {ck['gw_rss_mb']}MB")
if ck.get('ev_max_ms', 0) > 500:
    alerts.append(f"EV BLOCKED: {ck['ev_max_ms']}ms")
if ck.get('disk_pct', 0) > 90:
    alerts.append(f"DISK: {ck['disk_pct']}%")
if ck.get('sess_mb', 0) > 5:
    alerts.append(f"SESSIONS: {ck['sess_mb']}MB")
if ck.get('memory_kb', 0) > 100:
    alerts.append(f"MEMORY.md: {ck['memory_kb']}KB")

ck['alerts'] = alerts
ck['ts'] = time.time()

print(json.dumps(ck, indent=2))
for a in alerts:
    print(f"ALERT: {a}")
