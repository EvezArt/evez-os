#!/usr/bin/env python3
"""evez capability manifest - auto-documented by Round 3."""
import json,subprocess,importlib,pkgutil,time
from pathlib import Path
m={'ts':time.time(),'caps':{}}
try:
 r=subprocess.run(['openclaw','plugins','list'],capture_output=True,text=True,timeout=10)
 ps=[]
 for l in r.stdout.splitlines():
  if'│'in l and('enabled'in l or'disabled'in l):
   p=[x.strip()for x in l.split('│')]
   if len(p)>=6:ps.append({'name':p[1],'id':p[2],'status':p[4]})
 m['caps']['plugins']=ps
except:pass
pk=[]
for _,mn,_ in pkgutil.iter_modules():
 try:
  mod=importlib.import_module(mn);v=getattr(mod,'__version__','?')
  if v!='?':pk.append({'name':mn,'version':v})
 except:pass
m['caps']['python']=sorted(pk,key=lambda x:x['name'])
w=Path('/home/openclaw/.openclaw/workspace')
m['caps']['tools']=sorted([{'name':f.name,'size':f.stat().st_size}for f in w.glob('*.py')],key=lambda x:x['name'])
print(json.dumps(m,indent=2))
