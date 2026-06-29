#!/usr/bin/env python3
"""EVEZ Capability Discovery Engine"""
import json,os,sys,subprocess,importlib,pkgutil,ast,re,hashlib,time
from pathlib import Path
from datetime import datetime

W=Path('/home/openclaw/.openclaw/workspace')
H=Path.home()/'.openclaw'
C=H/'openclaw.json'

def scan_plugins():
    try:
        r=subprocess.run(['openclaw','plugins','list'],capture_output=True,text=True,timeout=10)
        ps=[]
        for l in r.stdout.splitlines():
            if '\u2502' in l and ('enabled' in l or 'disabled' in l):
                p=[x.strip() for x in l.split('\u2502')]
                if len(p)>=6: ps.append({'name':p[1],'id':p[2],'status':p[4]})
        return ps
    except Exception as e:
        return [{'error':str(e)}]

def scan_config():
    try: return json.load(open(C))
    except: return {}

def scan_skills():
    s=[]
    for b in [H/'plugin-skills',W/'skills']:
        if b.exists():
            for d in b.iterdir():
                if (d/'SKILL.md').exists(): s.append(d.name)
    return s

def scan_workspace_tools():
    t=[]
    for f in W.glob('*.py'):
        try:
            tr=ast.parse(f.read_text())
            fn=[n.name for n in ast.walk(tr) if isinstance(n,ast.FunctionDef)]
            if fn: t.append({'file':f.name,'functions':fn,'size':f.stat().st_size})
        except: pass
    return t

def scan_mesh():
    ns=[{'name':'vultr','ip':'207.148.12.53'},{'name':'gcp-west','ip':'34.53.51.34'},
         {'name':'gcp-small','ip':'34.23.192.213'},{'name':'gcp-power','ip':'35.222.248.151'},
         {'name':'gcp-openclaw','ip':'136.113.102.152'},{'name':'gcp-knot','ip':'136.118.144.227'}]
    for n in ns:
        try:
            r=subprocess.run(['curl','-s','-o','/dev/null','-w','%{http_code}','--max-time','3',f"http://{n['ip']}:18789/"],capture_output=True,text=True,timeout=5)
            n['gw']=r.stdout or 'timeout'
        except: n['gw']='error'
    return ns

def detect_inhibitions(plugins,cfg):
    inh=[]
    for p in plugins:
        if isinstance(p,dict) and p.get('status')=='disabled':
            inh.append({'type':'disabled_plugin','id':p.get('id','?'),'severity':'medium'})
    provs=cfg.get('models',{}).get('providers',{})
    for n,pr in provs.items():
        if not pr.get('apiKey'):
            inh.append({'type':'provider_no_key','name':n,'severity':'low'})
    if not cfg.get('channels'):
        inh.append({'type':'no_channels','severity':'critical','impact':'Cannot reach human'})
    try:
        r=subprocess.run(['openclaw','cron','list'],capture_output=True,text=True,timeout=10)
        if 'No cron' in r.stdout: inh.append({'type':'no_cron','severity':'high'})
    except: pass
    if not cfg.get('agents',{}).get('defaults',{}).get('sandbox'):
        inh.append({'type':'no_sandbox','severity':'medium'})
    sf=H/'agents'/'main'/'sessions'/'sessions.json'
    if sf.exists() and sf.stat().st_size>1000000:
        inh.append({'type':'session_bloat','size_mb':round(sf.stat().st_size/1048576,2),'severity':'medium'})
    for n,pr in provs.items():
        k=pr.get('apiKey','')
        if k and len(k)>10: inh.append({'type':'plaintext_key','name':n,'severity':'high'})
    return inh

EXPECTED={'web_search':['duckduckgo','tavily','searxng'],'messaging_telegram':['telegram'],'messaging_signal':['signal'],'messaging_sms':['sms'],'inbound_automation':['webhooks'],'active_memory':['active-memory'],'knowledge_vault':['memory-wiki'],'voice_tts':['elevenlabs','azure-speech','tts-local-cli'],'calendar':['google']}
EXPECTED_PY={'aiohttp':'Async HTTP','websockets':'WebSocket','PIL':'Image processing','matplotlib':'Plotting','pandas':'Data analysis','sqlalchemy':'SQL ORM','docker':'Docker SDK'}

def analyze_gaps(plugins,cfg):
    gaps=[]
    pids={p.get('id') for p in plugins if isinstance(p,dict)}
    for cap,spec in EXPECTED.items():
        found=any(pid in pids for pid in spec)
        enabled=any(next((p for p in plugins if isinstance(p,dict) and p.get('id')==pid),{}).get('status')=='enabled' for pid in spec)
        if not enabled: gaps.append({'capability':cap,'missing':not found,'disabled':found and not enabled,'fix':f"Enable: {','.join(spec)}"})
    for pkg,desc in EXPECTED_PY.items():
        try: importlib.import_module(pkg)
        except ImportError: gaps.append({'capability':f'py_{pkg}','fix':f'pip3 install --break-system-packages {pkg}','impact':desc})
    return gaps

def map_blindspots(cfg,plugins,gaps):
    bs=[]
    provs=cfg.get('models',{}).get('providers',{})
    for n,pr in provs.items():
        if not pr.get('apiKey'): bs.append({'type':'invisible_provider','name':n,'cost':'Silently fails'})
    gcaps={g['capability'] for g in gaps}
    for p in plugins:
        if isinstance(p,dict) and p.get('status')=='disabled':
            pid=p.get('id','')
            s=[]
            if pid in('duckduckgo','tavily','searxng') and 'web_search' in gcaps: s.append('search')
            if pid=='telegram' and 'messaging_telegram' in gcaps: s.append('telegram')
            if pid=='webhooks' and 'inbound_automation' in gcaps: s.append('automation')
            if pid=='active-memory' and 'active_memory' in gcaps: s.append('memory')
            if s: bs.append({'type':'disabled_solves_gap','name':pid,'solves':s,'cost':'Hidden connection'})
    for c in [{'cap':'proactive_messaging','chain':'cron+channel+send','cost':'3-step'},{'cap':'web_search','chain':'plugin+key+tool','cost':'3-step'},{'cap':'voice_output','chain':'tts+key+voice+output','cost':'4-step'}]:
        bs.append({'type':'capability_chain','capability':c['cap'],'chain':c['chain'],'cost':c['cost']})
    for s in [{'t':'session_accumulation','i':'Invisible growth','c':'No UI'},{'t':'api_key_plaintext','i':'Keys exposed','c':'Invisible until breach'},{'t':'plugin_overhead','i':'54 plugins many dead','c':'Blamed on slow'},{'t':'memory_bloat','i':'MEMORY.md unbounded','c':'Context fills faster'},{'t':'gateway_memory','i':'584MB no alert','c':'OOM no warning'}]:
        bs.append({'type':'system_hidden','subtype':s['t'],'issue':s['i'],'cost':s['c']})
    return bs

def forge_tools():
    ft=[]
    # Session cleanup
    (W/'evez_session_cleanup.py').write_text("""#!/usr/bin/env python3
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
""")
    ft.append('evez_session_cleanup.py')
    # Memory compactor
    (W/'evez_memory_compactor.py').write_text("""#!/usr/bin/env python3
from pathlib import Path
import re
M=Path('/home/openclaw/.openclaw/workspace/MEMORY.md')
A=Path('/home/openclaw/.openclaw/workspace/memory/MEMORY-ARCHIVE.md')
if not M.exists():exit(0)
lines=M.read_text().splitlines()
he=next((i for i,l in enumerate(lines)if l.startswith('### ')),0)
secs=[];cur={'h':'','l':[]}
for l in lines[he:]:
 if l.startswith('### '):
  if cur['h']:secs.append(cur)
  cur={'h':l,'l':[]}
 else:cur['l'].append(l)
if cur['h']:secs.append(cur)
keep=[s for s in secs if not re.search(r'2026-06-2[0-7]',s['h'])]
arch=[s for s in secs if re.search(r'2026-06-2[0-7]',s['h'])]
with open(M,'w')as f:
 for l in lines[:he]:f.write(l+'\n')
 for s in keep:f.write(s['h']+'\n')
 [f.write(l+'\n')for l in s['l']]
if arch:
 with open(A,'a')as f:
  f.write('\n--- Archived ---\n')
  for s in arch:f.write(s['h']+'\n')
  [f.write(l+'\n')for l in s['l']]
print(f'Kept {len(keep)}, archived {len(arch)}')
""")
    ft.append('evez_memory_compactor.py')
    # Config sync
    (W/'evez_config_sync.py').write_text("""#!/usr/bin/env python3
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
""")
    ft.append('evez_config_sync.py')
    # Health monitor
    (W/'evez_health_monitor.py').write_text("""#!/usr/bin/env python3
import json,subprocess,re,time
from pathlib import Path
ck={}
try:
 import psutil
 for p in psutil.process_iter(['pid','name','memory_info']):
  if'openclaw'in(p.info.get('name','')or''):ck['gw_rss_mb']=round(p.info['memory_info'].rss/1048576,1);break
except:pass
try:
 r=subprocess.run(['openclaw','status','--deep'],capture_output=True,text=True,timeout=15)
 for l in r.stdout.splitlines():
  if'max'in l and'p99'in l:
   m=re.search(r'max (\d+)ms.*p99 (\d+)ms.*util ([\d.]+)',l)
   if m:ck['ev_max_ms']=int(m.group(1));ck['ev_p99_ms']=int(m.group(2));ck['ev_util']=float(m.group(3))
except:pass
try:
 import psutil;u=psutil.disk_usage('/');ck['disk_pct']=u.percent;ck['disk_free_gb']=round(u.free/1073741824,1)
except:pass
sf=Path.home()/'.openclaw'/'agents'/'main'/'sessions'/'sessions.json'
if sf.exists():ck['sess_mb']=round(sf.stat().st_size/1048576,2)
alerts=[]
if ck.get('gw_rss_mb',0)>800:alerts.append('HIGH MEM')
if ck.get('ev_max_ms',0)>500:alerts.append('EV BLOCKED')
if ck.get('disk_pct',0)>90:alerts.append('DISK CRITICAL')
if ck.get('sess_mb',0)>5:alerts.append('SESSION BLOAT')
ck['alerts']=alerts;ck['ts']=time.time()
print(json.dumps(ck,indent=2))
for a in alerts:print(f'ALERT: {a}')
""")
    ft.append('evez_health_monitor.py')
    # Capability manifest
    (W/'evez_capability_manifest.py').write_text("""#!/usr/bin/env python3
import json,subprocess,importlib,pkgutil,time
from pathlib import Path
m={'ts':time.time(),'caps':{}}
try:
 r=subprocess.run(['openclaw','plugins','list'],capture_output=True,text=True,timeout=10)
 ps=[]
 for l in r.stdout.splitlines():
  if'\u2502'in l and('enabled'in l or'disabled'in l):
   p=[x.strip()for x in l.split('\u2502')]
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
""")
    ft.append('evez_capability_manifest.py')
    # Self-bootstrap
    (W/'evez_self_bootstrap.py').write_text("""#!/usr/bin/env python3
import importlib,subprocess,sys
from pathlib import Path
W=Path('/home/openclaw/.openclaw/workspace')
F=W/'tool-forge'
F.mkdir(exist_ok=True)
CAPS={'matplotlib':'data_viz','pandas':'data_analysis','aiohttp':'async_http','websockets':'ws_server','PIL':'image_proc','psycopg2':'postgres','redis':'cache','docker':'containers'}
def discover():
 g=[]
 for pkg,cap in CAPS.items():
  try:importlib.import_module(pkg)
  except ImportError:g.append((pkg,cap))
 return g
def main():
 gs=discover()
 if not gs:print('No gaps found.');return
 print(f'Found {len(gs)} gaps')
 for pkg,cap in gs:
  fn='forge_'+cap+'.py'
  c='#!/usr/bin/env python3\n'
  c+='import subprocess,sys\n'
  c+='if "--install" in sys.argv:\n'
  c+='    subprocess.run(["pip3","install","--break-system-packages","'+pkg+'"])\n'
  c+='elif "--verify" in sys.argv:\n'
  c+='    try:\n'
  c+='        __import__("'+pkg.replace('-','_')+'");print("INSTALLED")\n'
  c+='    except:print("MISSING")\n'
  (F/fn).write_text(c)
  print(f'Forged: {fn}')
 print(f'{len(gs)} tools in {F}/')
if __name__=='__main__':main()
""")
    ft.append('evez_self_bootstrap.py')
    return ft

def main():
    print('=== EVEZ CAPABILITY DISCOVERY ENGINE ===')
    print('Layer 1: Scanning...')
    plugins=scan_plugins()
    cfg=scan_config()
    skills=scan_skills()
    tools=scan_workspace_tools()
    mesh=scan_mesh()
    print(f'  Plugins:{len(plugins)} Skills:{len(skills)} Tools:{len(tools)} Nodes:{len(mesh)}')
    print('Layer 2: Inhibitions...')
    inh=detect_inhibitions(plugins,cfg)
    for i in inh:print(f"  [{i.get('severity','?').upper()}] {i['type']}: {i.get('name','')}")
    print('Layer 3: Gaps...')
    gaps=analyze_gaps(plugins,cfg)
    for g in gaps:print(f"  GAP: {g['capability']} -> {g.get('fix','?')}")
    print('Layer 4: Blindspots...')
    bs=map_blindspots(cfg,plugins,gaps)
    for b in bs:print(f"  BLIND: {b.get('type','?')} {b.get('issue',b.get('capability',''))} [{b.get('cost','?')}]")
    print('Layer 5: Forging tools...')
    ft=forge_tools()
    for t in ft:print(f'  FORGED: {t}')
    report={'timestamp':datetime.now().isoformat(),'plugins':len(plugins),'inhibitions':len(inh),'gaps':len(gaps),'blindspots':len(bs),'forged':len(ft)}
    (W/'capability-report.json').write_text(json.dumps(report,indent=2))
    print(f'Summary: {len(plugins)} plugins, {len(inh)} inhibitions, {len(gaps)} gaps, {len(bs)} blindspots, {len(ft)} tools forged')

if __name__=='__main__':
    main()
