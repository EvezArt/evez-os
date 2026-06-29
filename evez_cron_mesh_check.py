#!/usr/bin/env python3
"""Mesh health check cron job - runs every 15 min, logs to mesh-health.log."""
import json, subprocess, time
from pathlib import Path

NODES = [
    ('vultr', '207.148.12.53', 18789),
    ('gcp-west', '34.53.51.34', 18789),
    ('gcp-small', '34.23.192.213', 18789),
    ('gcp-power', '35.222.248.151', 18789),
    ('gcp-openclaw', '136.113.102.152', 18789),
    ('gcp-knot', '136.118.144.227', 18789),
]

log = Path('/home/openclaw/.openclaw/workspace/mesh-health.log')
results = {'ts': time.time(), 'nodes': []}

for name, ip, port in NODES:
    try:
        r = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '--max-time', '5',
             f'http://{ip}:{port}/'],
            capture_output=True, text=True, timeout=10
        )
        status = r.stdout or 'timeout'
    except:
        status = 'error'
    results['nodes'].append({'name': name, 'ip': ip, 'status': status})

down = [n['name'] for n in results['nodes'] if n['status'] != '200']
results['down'] = down
results['all_up'] = len(down) == 0

with open(log, 'a') as f:
    f.write(json.dumps(results) + chr(10))

if down:
    print(f'ALERT: Nodes down: {down}')
else:
    print(f'All {len(NODES)} nodes up')
