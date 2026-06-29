#!/usr/bin/env python3
"""Compact MEMORY.md - move old sections to archive."""
from pathlib import Path
import re, time

M = Path('/home/openclaw/.openclaw/workspace/MEMORY.md')
A = Path('/home/openclaw/.openclaw/workspace/memory/MEMORY-ARCHIVE.md')
if not M.exists():
    exit(0)

lines = M.read_text().splitlines()
he = next((i for i, l in enumerate(lines) if l.startswith('### ')), 0)

secs = []
cur = {'h': '', 'l': []}
for l in lines[he:]:
    if l.startswith('### '):
        if cur['h']:
            secs.append(cur)
        cur = {'h': l, 'l': []}
    else:
        cur['l'].append(l)
if cur['h']:
    secs.append(cur)

keep = [s for s in secs if not re.search(r'2026-06-2[0-7]', s['h'])]
arch = [s for s in secs if re.search(r'2026-06-2[0-7]', s['h'])]

with open(M, 'w') as f:
    for l in lines[:he]:
        f.write(l + chr(10))
    for s in keep:
        f.write(s['h'] + chr(10))
        for l in s['l']:
            f.write(l + chr(10))

if arch:
    with open(A, 'a') as f:
        f.write(chr(10) + '--- Archived ' + str(int(time.time())) + ' ---' + chr(10))
        for s in arch:
            f.write(s['h'] + chr(10))
            for l in s['l']:
                f.write(l + chr(10))

print(f'Compacted: kept {len(keep)}, archived {len(arch)}')
