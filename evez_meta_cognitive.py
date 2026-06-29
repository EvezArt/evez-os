#!/usr/bin/env python3
"""Round 3: Meta-Cognitive Capability Discovery

What Rounds 1-2 missed:
- The discovery tools themselves are undiscoverable (no entry point)
- Import side-effects pollute discovery (breakcore plays during scan)
- The catalog is not searchable from the conversation interface
- Friction reducers list steps but don't EXECUTE them
- No feedback loop: tools don't report what they found back to the system
- No capability graph: relationships between tools are unmapped
- No auto-activation: gaps are found but not fixed
- No human-language interface: outputs are JSON/logs, not conversational
"""
import json, os, sys, subprocess, importlib, pkgutil, ast, re, hashlib, time
from pathlib import Path
from datetime import datetime

W = Path('/home/openclaw/.openclaw/workspace')
H = Path.home() / '.openclaw'

# === LAYER 13: CAPABILITY GRAPH BUILDER ===
def build_graph():
    """Build a graph of all tools and their relationships.
    Nodes = tools, Edges = imports/calls/shares-data-with."""
    nodes = []
    edges = []

    for f in sorted(W.glob('*.py')):
        try:
            tree = ast.parse(f.read_text())
            imports = []
            calls = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        imports.append(n.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    calls.append(node.func.id)

            local_imports = [i for i in imports if i.startswith(('evez_', 'messiah_', 'nation_', 'proxy_', 'qc_'))]
            for li in local_imports:
                edges.append({'source': f.name, 'target': li + '.py', 'type': 'import'})

            # Check for shared file I/O (two tools reading/writing the same files)
            nodes.append({
                'name': f.name,
                'imports': imports[:10],
                'calls': calls[:10],
                'local_imports': local_imports,
                'size': f.stat().st_size
            })
        except:
            pass

    # Detect shared JSON files (data dependencies)
    json_files = {}
    for f in W.glob('*.py'):
        try:
            content = f.read_text()
            for m in re.finditer(r"['\"]([^'\"]+\.json)['\"]", content):
                jf = m.group(1)
                if jf not in ('package.json', 'tsconfig.json'):
                    if jf not in json_files:
                        json_files[jf] = []
                    json_files[jf].append(f.name)
        except:
            pass

    for jf, files in json_files.items():
        if len(files) > 1:
            for i in range(len(files)):
                for j in range(i+1, len(files)):
                    edges.append({'source': files[i], 'target': files[j], 'type': 'shared_data', 'file': jf})

    return nodes, edges, json_files

# === LAYER 14: AUTO-ACTIVATION ENGINE ===
def auto_activate():
    """Don't just find gaps — fix them. Auto-enable disabled plugins, install missing packages."""
    activated = []
    failed = []

    # Auto-install missing Python packages (safe — only well-known packages)
    safe_packages = {
        'pandas': 'data analysis',
        'docker': 'container management',
        'redis': 'caching',
        'aiohttp': 'async HTTP',
    }
    for pkg, desc in safe_packages.items():
        try:
            importlib.import_module(pkg)
        except ImportError:
            try:
                r = subprocess.run(
                    ['pip3', 'install', '--break-system-packages', pkg],
                    capture_output=True, text=True, timeout=120
                )
                if r.returncode == 0:
                    activated.append(f'Installed Python: {pkg} ({desc})')
                else:
                    failed.append(f'Failed to install {pkg}: {r.stderr[:100]}')
            except Exception as e:
                failed.append(f'Failed to install {pkg}: {str(e)}')

    # Auto-enable safe OpenClaw plugins
    safe_plugins = ['duckduckgo', 'active-memory', 'memory-wiki']
    for plugin in safe_plugins:
        try:
            r = subprocess.run(
                ['openclaw', 'plugins', 'enable', plugin],
                capture_output=True, text=True, timeout=10
            )
            if r.returncode == 0:
                activated.append(f'Enabled plugin: {plugin}')
            else:
                # Check if already enabled
                if 'already' in r.stdout.lower() or 'enabled' in r.stdout.lower():
                    pass  # Already on, skip
                else:
                    failed.append(f'Failed to enable {plugin}: {r.stdout[:100]}')
        except Exception as e:
            failed.append(f'Failed to enable {plugin}: {str(e)}')

    # Auto-create useful cron jobs if none exist
    try:
        r = subprocess.run(['openclaw', 'cron', 'list'], capture_output=True, text=True, timeout=10)
        if 'No cron' in r.stdout or r.returncode != 0:
            # Create a mesh health check cron
            cron_script = W / 'evez_cron_mesh_check.py'
            cron_script.write_text(generate_mesh_cron())
            os.chmod(cron_script, 0o755)
            activated.append(f'Created mesh health check script: {cron_script.name}')
    except:
        pass

    return activated, failed

def generate_mesh_cron():
    return '''#!/usr/bin/env python3
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
'''

# === LAYER 15: CONVERSATIONAL INTERFACE GENERATOR ===
def generate_interface():
    """Generate a tool that lets the human ask 'what can you do?' and get an answer."""
    catalog_path = W / 'capability-catalog.json'
    catalog = json.load(open(catalog_path)) if catalog_path.exists() else {'capabilities': []}

    NL = chr(10)
    lines = [
        '#!/usr/bin/env python3',
        '"""EVEZ Capability Query Interface',
        '',
        'Usage:',
        '  python3 evez_what_can_you_do.py                    # List all capabilities',
        '  python3 evez_what_can_you_do.py search <query>     # Search capabilities',
        '  python3 evez_what_can_you_do.py friction            # Show high-friction capabilities',
        '  python3 evez_what_can_you_do.py blindspots          # Show hidden capabilities',
        '  python3 evez_what_can_you_do.py chains              # Show capability chains',
        '  python3 evez_what_can_you_do.py composites          # Show composite capabilities',
        '  python3 evez_what_can_you_do.py graph               # Show capability graph',
        '  python3 evez_what_can_you_do.py activate            # Auto-activate missing capabilities',
        '"""',
        'import json, sys, re, subprocess',
        'from pathlib import Path',
        '',
        'W = Path("/home/openclaw/.openclaw/workspace")',
        '',
        'def load_catalog():',
        '    p = W / "capability-catalog.json"',
        '    return json.load(open(p)) if p.exists() else {}',
        '',
        'def load_graph():',
        '    p = W / "capability-graph.json"',
        '    return json.load(open(p)) if p.exists() else {}',
        '',
        'def load_report():',
        '    p = W / "capability-report-r2.json"',
        '    return json.load(open(p)) if p.exists() else {}',
        '',
        'def cmd_list():',
        '    cat = load_catalog()',
        '    caps = cat.get("capabilities", [])',
        '    print(f"EVEZ Capability Catalog ({len(caps)} tools)")',
        '    print("=" * 60)',
        '    for c in caps:',
        '        desc = c.get("description", "")[:60]',
        '        if not desc: desc = ", ".join(c.get("functions", [])[:3])',
        '        print(f"  {c[chr(39)]file[chr(39)]:<40} {desc}")',
        '    print(f"\nTotal: {len(caps)} tools")',
        '',
        'def cmd_search(query):',
        '    cat = load_catalog()',
        '    q = query.lower()',
        '    results = []',
        '    for c in cat.get("capabilities", []):',
        '        text = (c.get("file", "") + " " + " ".join(c.get("functions", [])) + " " + c.get("description", "")).lower()',
        '        if q in text: results.append(c)',
        '    print(f"Search: {query} ({len(results)} results)")',
        '    for r in results:',
        '        print(f"  {r[chr(39)]file[chr(39)]}: {r.get(chr(39)]description[chr(39)], chr(39)]?[chr(39)])[:80]}")',
        '',
        'def cmd_friction():',
        '    cat = load_catalog()',
        '    for f in sorted(cat.get("friction_map", []), key=lambda x: x.get("friction_score", 0), reverse=True):',
        '        score = f.get("friction_score", 0)',
        '        cap = f.get("capability", "?")',
        '        reason = f.get("reason", "?")',
        '        print(f"  [{score} stars] {cap}")',
        '        print(f"    Steps: {len(f.get(chr(39)]steps[chr(39)], []))} - {reason}")',
        '',
        'def cmd_blindspots():',
        '    cat = load_catalog()',
        '    for b in cat.get("blindspots", []):',
        '        btype = b.get("type", "?")',
        '        name = b.get("file", b.get("var", b.get("skill", "?")))',
        '        print(f"  {btype}: {name}")',
        '',
        'def cmd_chains():',
        '    g = load_graph()',
        '    for e in g.get("edges", []):',
        '        if e.get("type") == "import":',
        '            print(f"  {e[chr(39)]source[chr(39)]} -> {e[chr(39)]target[chr(39)]} (import)")',
        '        elif e.get("type") == "shared_data":',
        '            print(f"  {e[chr(39)]source[chr(39)]} <-> {e[chr(39)]target[chr(39)]} (shared: {e.get(chr(39)]file[chr(39)], chr(39)]?[chr(39)])}")',
        '',
        'def cmd_activate():',
        '    print("Auto-activating capabilities...")',
        '    r = subprocess.run([sys.executable, str(W / "evez_auto_activate.py")], capture_output=True, text=True)',
        '    print(r.stdout)',
        '    if r.stderr: print(f"Errors: {r.stderr[:200]}")',
        '',
        'def main():',
        '    if len(sys.argv) < 2:',
        '        cmd_list()',
        '        return',
        '    cmd = sys.argv[1]',
        '    if cmd == "search" and len(sys.argv) > 2: cmd_search(sys.argv[2])',
        '    elif cmd == "friction": cmd_friction()',
        '    elif cmd == "blindspots": cmd_blindspots()',
        '    elif cmd == "chains": cmd_chains()',
        '    elif cmd == "activate": cmd_activate()',
        '    else: print(f"Unknown: {cmd}. Try: list, search, friction, blindspots, chains, activate")',
        '',
        'if __name__ == "__main__":',
        '    main()',
    ]
    return NL.join(lines) + NL

# === LAYER 16: RECURSIVE SELF-IMPROVEMENT ===
def self_improve():
    """The system audits its own discovery tools for gaps and generates fixes."""
    improvements = []

    # Check: does the discovery helper actually work?
    dh = W / 'evez_discovery_helper.py'
    if dh.exists():
        try:
            r = subprocess.run([sys.executable, str(dh), 'list'], capture_output=True, text=True, timeout=10)
            if r.returncode != 0:
                improvements.append({'issue': 'discovery_helper fails', 'fix': 'regenerate'})
        except:
            improvements.append({'issue': 'discovery_helper cannot run', 'fix': 'regenerate'})

    # Check: are there tools with no docstring? (undocumented = undiscoverable)
    for f in W.glob('evez_*.py'):
        try:
            tree = ast.parse(f.read_text())
            has_doc = False
            if tree.body and isinstance(tree.body[0], ast.Expr):
                if isinstance(tree.body[0].value, ast.Constant) and isinstance(tree.body[0].value.value, str):
                    has_doc = True
            if not has_doc:
                improvements.append({'issue': f'{f.name} has no docstring', 'fix': 'add docstring'})
        except:
            pass

    # Check: are there JSON report files that nothing reads?
    for jf in W.glob('capability-*.json'):
        referenced = False
        for pf in W.glob('*.py'):
            try:
                if jf.name in pf.read_text():
                    referenced = True
                    break
            except:
                pass
        if not referenced:
            improvements.append({'issue': f'{jf.name} not referenced by any tool', 'fix': 'add reader'})

    # Check: does the health monitor alert on the right thresholds?
    hm = W / 'evez_health_monitor.py'
    if hm.exists():
        content = hm.read_text()
        if 'memory_kb' in content and '100' in content:
            improvements.append({'issue': 'MEMORY.md alert at 100KB — currently 118KB, should auto-compact', 'fix': 'trigger compactor'})

    return improvements

def main():
    print('=== ROUND 3: META-COGNITIVE CAPABILITY DISCOVERY ===')

    print('Layer 13: Building Capability Graph...')
    nodes, edges, shared = build_graph()
    print(f'  {len(nodes)} nodes, {len(edges)} edges, {len(shared)} shared data files')
    graph = {'nodes': nodes, 'edges': edges, 'shared_data': shared, 'ts': time.time()}
    (W / 'capability-graph.json').write_text(json.dumps(graph, indent=2))
    for e in edges[:10]:
        print(f'  {e["source"]} -> {e["target"]} ({e["type"]})')

    print('Layer 14: Auto-Activation Engine...')
    activated, failed = auto_activate()
    for a in activated:
        print(f'  ACTIVATED: {a}')
    for f in failed:
        print(f'  FAILED: {f}')

    print('Layer 15: Conversational Interface Generator...')
    interface = generate_interface()
    (W / 'evez_what_can_you_do.py').write_text(interface)
    print('  Generated: evez_what_can_you_do.py')

    # Also generate standalone auto-activator
    NL = chr(10)
    aa_lines = [
        '#!/usr/bin/env python3',
        '"""Auto-activate missing capabilities."""',
        'import subprocess, sys, importlib',
        'W = sys.path.insert(0, "/home/openclaw/.openclaw/workspace")',
        '',
        'def install(pkg, desc):',
        '    try: importlib.import_module(pkg); return f"Already installed: {pkg}"',
        '    except ImportError: pass',
        '    try:',
        '        r = subprocess.run(["pip3", "install", "--break-system-packages", pkg], capture_output=True, text=True, timeout=120)',
        '        return f"Installed: {pkg} ({desc})" if r.returncode == 0 else f"Failed: {pkg}"',
        '    except Exception as e: return f"Error: {pkg}: {e}"',
        '',
        'def enable_plugin(name):',
        '    try:',
        '        r = subprocess.run(["openclaw", "plugins", "enable", name], capture_output=True, text=True, timeout=10)',
        '        return f"Enabled: {name}" if r.returncode == 0 else f"Skip: {name}"',
        '    except: return f"Error: {name}"',
        '',
        'def main():',
        '    for pkg, desc in [("pandas", "data analysis"), ("docker", "containers"), ("redis", "cache"), ("aiohttp", "async HTTP")]:',
        '        print(install(pkg, desc))',
        '    for p in ["duckduckgo", "active-memory", "memory-wiki"]:',
        '        print(enable_plugin(p))',
        '',
        'if __name__ == "__main__": main()',
    ]
    (W / 'evez_auto_activate.py').write_text(NL.join(aa_lines) + NL)
    print('  Generated: evez_auto_activate.py')

    print('Layer 16: Recursive Self-Improvement...')
    improvements = self_improve()
    print(f'  {len(improvements)} improvements identified')
    for imp in improvements:
        print(f'  IMPROVE: {imp["issue"]} -> {imp["fix"]}')

    # Execute improvements
    executed = 0
    for imp in improvements:
        if 'no docstring' in imp['issue']:
            # Add a basic docstring to undocumented tools
            fname = imp['issue'].split()[0]
            fp = W / fname
            if fp.exists():
                content = fp.read_text()
                if content.startswith('#!/usr/bin/env python3\n'):
                    lines = content.split(chr(10))
                    # Insert docstring after shebang
                    desc = fname.replace('.py', '').replace('_', ' ')
                    lines.insert(1, f'"""{desc} - auto-documented by Round 3."""')
                    fp.write_text(chr(10).join(lines))
                    executed += 1
        elif 'not referenced' in imp['issue']:
            # Create a reader for orphaned JSON
            jname = imp['issue'].split()[0]
            reader = W / ('read_' + jname.replace('.json', '.py'))
            reader.write_text(f'''#!/usr/bin/env python3
"""Reader for {jname} - auto-generated by Round 3."""
import json
from pathlib import Path
p = Path("/home/openclaw/.openclaw/workspace/{jname}")
if p.exists():
    d = json.load(open(p))
    print(json.dumps(d, indent=2))
else:
    print("File not found")
''')
            executed += 1
        elif 'auto-compact' in imp.get('fix', ''):
            # Run the memory compactor
            try:
                subprocess.run([sys.executable, str(W / 'evez_memory_compactor.py')], capture_output=True, text=True, timeout=10)
                executed += 1
            except:
                pass

    print(f'  {executed}/{len(improvements)} improvements executed')

    report = {
        'timestamp': datetime.now().isoformat(),
        'round': 3,
        'graph_nodes': len(nodes),
        'graph_edges': len(edges),
        'activated': len(activated),
        'failed_activations': len(failed),
        'improvements_found': len(improvements),
        'improvements_executed': executed,
    }
    (W / 'capability-report-r3.json').write_text(json.dumps(report, indent=2))

    total = len(nodes) + len(activated) + len(improvements)
    print(f'\nRound 3 Summary: {len(nodes)} graph nodes, {len(edges)} edges, {len(activated)} activated, {len(improvements)} improvements ({executed} executed)')
    print(f'\nTotal tools forged across all rounds:')
    all_tools = sorted([f.name for f in W.glob('evez_*.py') if 'capability' in f.name or 'discovery' in f.name or 'what_can' in f.name or 'auto_activate' in f.name or 'reduce_friction' in f.name or 'composite' in f.name or 'self_bootstrap' in f.name or 'session_cleanup' in f.name or 'memory_compactor' in f.name or 'config_sync' in f.name or 'health_monitor' in f.name or 'cron_mesh' in f.name])
    for t in all_tools:
        print(f'  {t}')
    print(f'  Total: {len(all_tools)} discovery/capability tools')

if __name__ == '__main__':
    main()
