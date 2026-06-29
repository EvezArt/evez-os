#!/usr/bin/env python3
"""evez config sync - auto-documented by Round 3."""
import json,shutil,hashlib
from pathlib import Path
C=Path.home()/'.openclaw'/'openclaw.json'
if not C.exists():exit(1)
d=json.load(open(C))
t=C.with_suffix('.json.tmp')
json.dump(d,open(t,'w'),indent=2)
t.replace(C)
shutil.copy2(C,C.with_suffix('.json.bak'))
shutil.copy2(C,C.with_suffix('.json.last-good'))
print(f'Config synced ({hashlib.sha256(C.read_bytes()).hexdigest()[:16]})')
