#!/usr/bin/env python3
"""evez session cleanup - auto-documented by Round 3."""
import json,time
from pathlib import Path
S=Path.home()/'.openclaw'/'agents'/'main'/'sessions'
sf=S/'sessions.json'
if not sf.exists():exit(0)
now=time.time();c=0
for f in S.glob('*.jsonl*'):
 if f.is_file()and(now-f.stat().st_mtime)/3600>24:
  if any(x in f.name for x in['.reset.','.deleted.','.corrupt']):f.unlink();c+=1
d=json.load(open(sf))
sess=d if isinstance(d,list)else d.get('sessions',d)
if isinstance(sess,dict):
 sk=[k for k in sess if'subagent'in k]
 if len(sk)>10:
  for k in sorted(sk)[:-10]:del sess[k]
  c+=len(sk)-10
json.dump(d,open(sf,'w'))
print(f'Cleaned {c} items')
