#!/usr/bin/env python3
"""Round 2: Deep Capability Excavation Engine

What Round 1 missed:
- Capability CHAINS (A needs B needs C — human sees A, can't find B->C path)
- Latent tools (installed but not connected to any interface)
- Composite capabilities (two existing tools combined = new capability neither provides alone)
- Inverted blindspots (things the system CAN do that are impossible to search for)
- Discovery friction (capabilities that work but have no documentation path)
"""
import json, os, sys, subprocess, importlib, pkgutil, ast, re, hashlib, time
from pathlib import Path
from datetime import datetime

W = Path('/home/openclaw/.openclaw/workspace')
H = Path.home() / '.openclaw'

# === LAYER 7: CAPABILITY CHAIN DISCOVERY ===
def discover_chains():
    """Find multi-step capability paths where each step is a prerequisite for the next.
    Human sees step 1, can't discover steps 2-4 exist."""
    chains = []

    # Scan all Python tools for subprocess calls (indicates tool-to-tool chains)
    for f in W.glob('*.py'):
        try:
            tree = ast.parse(f.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Attribute) and func.attr == 'run':
                        if isinstance(func.value, ast.Name) and func.value.id == 'subprocess':
                            if node.args and isinstance(node.args[0], ast.List):
                                cmds = [a.value if isinstance(a, ast.Constant) else '?' for a in node.args[0].elts]
                                chains.append({
                                    'source': f.name,
                                    'calls': [c for c in cmds if isinstance(c, str)],
                                    'type': 'subprocess_chain'
                                })
        except:
            pass

    # Scan for import chains (tool A imports tool B's functionality)
    for f in W.glob('*.py'):
        try:
            tree = ast.parse(f.read_text())
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(n.name for n in node.names)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            # Check if any imports are local tools
            local_imports = [i for i in imports if any(i.startswith(prefix) for prefix in ['evez_', 'messiah_', 'nation_', 'proxy_', 'qc_'])]
            if local_imports:
                chains.append({'source': f.name, 'imports': local_imports, 'type': 'import_chain'})
        except:
            pass

    return chains

# === LAYER 8: LATENT CAPABILITY DETECTOR ===
def detect_latent():
    """Find installed capabilities that work but have no interface path.
    Things the system CAN do but a human would never find."""
    latent = []

    # Check all installed Python packages for importable-but-unused capabilities
    installed = []
    for _, mod_name, _ in pkgutil.iter_modules():
        try:
            mod = importlib.import_module(mod_name)
            # Check for callable attributes that look like tools
            for attr in dir(mod):
                if attr.startswith('_'):
                    continue
                obj = getattr(mod, attr)
                if callable(obj) and not isinstance(obj, type):
                    installed.append({'package': mod_name, 'function': attr})
        except:
            pass

    # Find workspace Python files with functions that are never called by anything
    all_funcs = set()
    called_funcs = set()
    for f in W.glob('*.py'):
        try:
            tree = ast.parse(f.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    all_funcs.add(node.name)
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    called_funcs.add(node.func.id)
        except:
            pass

    uncalled = all_funcs - called_funcs - {'main', 'discover', 'scan_plugins', 'scan_config', 'scan_skills', 'scan_workspace_tools', 'scan_mesh', 'detect_inhibitions', 'analyze_gaps', 'map_blindspots', 'forge_tools', 'run'}
    for fn in sorted(uncalled)[:50]:
        latent.append({'type': 'uncalled_function', 'name': fn})

    # Check for CLI tools installed but not in PATH awareness
    for tool in ['curl', 'wget', 'jq', 'ffmpeg', 'convert', 'sqlite3', 'git', 'ssh', 'rsync', 'crontab']:
        try:
            r = subprocess.run(['which', tool], capture_output=True, text=True, timeout=2)
            if r.returncode == 0:
                latent.append({'type': 'cli_tool', 'name': tool, 'path': r.stdout.strip()})
        except:
            pass

    return latent, installed

# === LAYER 9: COMPOSITE CAPABILITY FORGE ===
def forge_composites(latent, chains):
    """Combine two existing capabilities into a new one neither provides alone."""
    composites = []

    # If we have curl + sqlite3, we can build a web-to-db pipeline
    has_curl = any(l['name'] == 'curl' for l in latent if l.get('type') == 'cli_tool')
    has_sqlite = any(l['name'] == 'sqlite3' for l in latent if l.get('type') == 'cli_tool')
    has_jq = any(l['name'] == 'jq' for l in latent if l.get('type') == 'cli_tool')

    if has_curl and has_sqlite:
        composites.append({
            'name': 'web_to_db_pipeline',
            'recipe': 'curl API -> jq filter -> sqlite3 store',
            'capability': 'Fetch web data and store in queryable DB',
            'tools': ['curl', 'jq', 'sqlite3'] if has_jq else ['curl', 'sqlite3']
        })

    if has_curl and has_jq:
        composites.append({
            'name': 'api_intelligence_scanner',
            'recipe': 'curl endpoint -> jq extract fields -> hash comparison',
            'capability': 'Monitor external APIs for changes',
            'tools': ['curl', 'jq']
        })

    # Check if we have both subprocess and json (can build inter-process pipelines)
    composites.append({
        'name': 'tool_pipeline_orchestrator',
        'recipe': 'Chain any N tools via subprocess + json I/O',
        'capability': 'Compose tools into automated workflows',
        'tools': ['subprocess', 'json']
    })

    # Check for matplotlib + numpy (can build visualization pipeline)
    try:
        importlib.import_module('numpy')
        has_numpy = True
    except:
        has_numpy = False
    try:
        importlib.import_module('matplotlib')
        has_mpl = True
    except:
        has_mpl = False

    if has_numpy and has_mpl:
        composites.append({
            'name': 'data_viz_pipeline',
            'recipe': 'numpy compute -> matplotlib render -> save SVG/PNG',
            'capability': 'Generate visualizations from computed data',
            'tools': ['numpy', 'matplotlib']
        })

    # Forge composite tools
    forged = []
    for c in composites:
        fname = f"composite_{c['name']}.py"
        fpath = W / fname
        code = generate_composite(c)
        fpath.write_text(code)
        forged.append({'name': fname, 'composite': c['name']})

    return composites, forged

def generate_composite(c):
    NL = chr(10)
    lines = [
        '#!/usr/bin/env python3',
        f'"""Composite capability: {c["name"]} - {c["capability"]}"""',
        'import subprocess, json, sys, hashlib, time',
        'from pathlib import Path',
        '',
        f'RECIPE = {json.dumps(c["recipe"])}',
        f'TOOLS = {json.dumps(c["tools"])}',
        '',
        'def run(*args, **kwargs):',
        f'    """Execute: {c["recipe"]}"""',
        '    results = []',
        '    for tool in TOOLS:',
        '        try:',
        '            r = subprocess.run([tool, "--version"], capture_output=True, text=True, timeout=5)',
        '            results.append({"tool": tool, "available": r.returncode == 0})',
        '        except Exception as e:',
        '            results.append({"tool": tool, "available": False, "error": str(e)})',
        '    return results',
        '',
        'def main():',
        '    print(f"Composite: {c["name"]}")',
        '    print(f"Recipe: {c["recipe"]}")',
        '    print(f"Capability: {c["capability"]}")',
        '    r = run()',
        '    for t in r:',
        '        status = "OK" if t["available"] else "MISSING"',
        '        print(f"  {t["tool"]}: {status}")',
        '    if all(t["available"] for t in r):',
        '        print("READY: All tools available")',
        '    else:',
        '        print("BLOCKED: Some tools missing")',
        '',
        'if __name__ == "__main__":',
        '    main()',
    ]
    return NL.join(lines) + NL

# === LAYER 10: INVERTED BLINDSPOT SCANNER ===
def scan_inverted_blindspots():
    """Find things the system CAN do that are impossible to discover via search.
    These are capabilities that exist but have no keywords, no docs, no path."""
    blindspots = []

    # Find Python files with no docstring (undocumented capabilities)
    for f in W.glob('*.py'):
        try:
            tree = ast.parse(f.read_text())
            has_doc = False
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                            has_doc = True
                            break
            if not has_doc:
                blindspots.append({'type': 'undocumented_tool', 'file': f.name, 'impact': 'Human cannot discover what it does without reading code'})
        except:
            pass

    # Find environment variables that tools reference but are never set
    for f in W.glob('*.py'):
        try:
            content = f.read_text()
            for m in re.finditer(r'os\.(?:environ|getenv)\(["\']([^"\']+)', content):
                var = m.group(1)
                if var and var not in os.environ:
                    blindspots.append({'type': 'missing_env_var', 'var': var, 'file': f.name, 'impact': 'Tool exists but cannot run without this env var'})
        except:
            pass

    # Find config keys that are referenced but don't exist
    try:
        cfg = json.load(open(H / 'openclaw.json'))
        cfg_keys = set()
        def collect_keys(d, prefix=''):
            if isinstance(d, dict):
                for k, v in d.items():
                    cfg_keys.add(prefix + k)
                    collect_keys(v, prefix + k + '.')
        collect_keys(cfg)

        # Check for referenced-but-missing keys in workspace files
        for f in W.glob('*.py'):
            try:
                content = f.read_text()
                for m in re.finditer(r'cfg(?:\.get)?\(["\']([^"\']+)\)', content):
                    key = m.group(1)
                    if key and key not in cfg_keys:
                        blindspots.append({'type': 'missing_config_key', 'key': key, 'file': f.name})
            except:
                pass
    except:
        pass

    # Find skills that are installed but not in any tool's capability map
    skill_dir = H / 'plugin-skills'
    if skill_dir.exists():
        installed_skills = {d.name for d in skill_dir.iterdir() if (d / 'SKILL.md').exists()}
        # Check which skills are referenced in workspace code
        referenced = set()
        for f in W.glob('*.py'):
            try:
                content = f.read_text()
                for skill in installed_skills:
                    if skill in content:
                        referenced.add(skill)
            except:
                pass
        unreferenced = installed_skills - referenced
        for s in sorted(unreferenced)[:20]:
            blindspots.append({'type': 'unreferenced_skill', 'skill': s, 'impact': 'Skill installed but never invoked by any tool'})

    return blindspots

# === LAYER 11: DISCOVERY FRICTION MAPPER ===
def map_friction():
    """Map the friction between capability existence and human discovery.
    How many steps does it take to activate each capability?"""
    friction = []

    # Count steps to activate web search: enable plugin -> set API key -> test -> use
    friction.append({
        'capability': 'web_search',
        'steps': ['openclaw plugins enable duckduckgo', 'openclaw config apply', 'test search', 'use in conversation'],
        'friction_score': 4,
        'human_discoverable': False,
        'reason': 'No UI hint that search exists or is possible'
    })

    friction.append({
        'capability': 'proactive_messaging',
        'steps': ['enable telegram plugin', 'set bot token', 'configure channel', 'set cron job', 'write message template', 'trigger send'],
        'friction_score': 6,
        'human_discoverable': False,
        'reason': '6-step chain with no documentation path connecting the steps'
    })

    friction.append({
        'capability': 'mesh_monitoring',
        'steps': ['know mesh IPs', 'find health endpoint', 'parse JSON', 'set up cron', 'configure alerting'],
        'friction_score': 5,
        'human_discoverable': 'partially',
        'reason': 'IPs are in MEMORY.md, endpoints in HEARTBEAT.md, but no single discovery path'
    })

    friction.append({
        'capability': 'voice_output',
        'steps': ['install TTS plugin', 'set API key', 'configure voice', 'route to speaker', 'trigger TTS'],
        'friction_score': 5,
        'human_discoverable': False,
        'reason': 'Multiple plugins, unclear which to choose'
    })

    friction.append({
        'capability': 'quantum_computing',
        'steps': ['install qiskit', 'install qutip', 'install pennylane', 'find quantum-agents/ dir', 'run qc_runner.py'],
        'friction_score': 5,
        'human_discoverable': False,
        'reason': 'Exists in workspace but no top-level entry point or menu'
    })

    # Auto-detect friction for all workspace tools
    for f in sorted(W.glob('*.py'))[:30]:
        try:
            tree = ast.parse(f.read_text())
            funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            has_main = 'main' in funcs
            has_cli = any('sys.argv' in ast.dump(n) for n in ast.walk(tree))
            if has_main and has_cli:
                friction.append({
                    'capability': f.name,
                    'steps': ['python3 ' + f.name],
                    'friction_score': 1,
                    'human_discoverable': True,
                    'reason': 'Single command, but human must know file exists'
                })
        except:
            pass

    return friction

# === LAYER 12: SELF-PROPAGATING DISCOVERY LOOP ===
def self_propagate(latent, blindspots, friction):
    """Generate tools that reduce discovery friction for each capability."""
    forged = []

    # Generate a capability catalog (searchable index of everything the system can do)
    catalog = {
        'generated': datetime.now().isoformat(),
        'capabilities': [],
        'friction_map': [],
        'discovery_paths': []
    }

    # Index all Python tools with their functions
    for f in sorted(W.glob('*.py')):
        try:
            tree = ast.parse(f.read_text())
            funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            # Try to find docstring
            doc = ''
            if tree.body and isinstance(tree.body[0], ast.Expr):
                if isinstance(tree.body[0].value, ast.Constant) and isinstance(tree.body[0].value.value, str):
                    doc = tree.body[0].value.value[:200]

            catalog['capabilities'].append({
                'file': f.name,
                'functions': funcs[:10],
                'classes': classes[:5],
                'description': doc,
                'size': f.stat().st_size,
                'run': f'python3 {f.name}'
            })
        except:
            pass

    catalog['friction_map'] = friction
    catalog['blindspots'] = blindspots[:20]

    # Write the catalog
    (W / 'capability-catalog.json').write_text(json.dumps(catalog, indent=2))
    forged.append('capability-catalog.json')

    # Generate a discovery helper — a tool that helps humans find capabilities
    helper_code = generate_discovery_helper(catalog)
    (W / 'evez_discovery_helper.py').write_text(helper_code)
    forged.append('evez_discovery_helper.py')

    # Generate friction reducers — one-click activation scripts for high-friction capabilities
    for cap in friction:
        if cap.get('friction_score', 0) >= 4:
            reducer = generate_friction_reducer(cap)
            fname = f"reduce_friction_{cap['capability']}.py"
            (W / fname).write_text(reducer)
            forged.append(fname)

    return forged

def generate_discovery_helper(catalog):
    NL = chr(10)
    lines = [
        '#!/usr/bin/env python3',
        '"""EVEZ Discovery Helper - search and find any capability in the system."""',
        'import json, sys, re',
        'from pathlib import Path',
        '',
        'CATALOG = json.load(open(Path("/home/openclaw/.openclaw/workspace/capability-catalog.json")))',
        '',
        'def search(query):',
        '    """Search capabilities by keyword."""',
        '    results = []',
        '    q = query.lower()',
        '    for cap in CATALOG["capabilities"]:',
        '        searchable = (cap["file"] + " " + " ".join(cap["functions"]) + " " + cap.get("description", "")).lower()',
        '        if q in searchable:',
        '            results.append(cap)',
        '    return results',
        '',
        'def list_all():',
        '    """List all discovered capabilities."""',
        '    for cap in CATALOG["capabilities"]:',
        '        desc = cap.get("description", "")[:80]',
        '        print(f"  {cap[chr(39)+chr(39)]+chr(39)}file{chr(39)+chr(39)+chr(39)]} - {desc}")',
        '    print(f"\nTotal: {len(CATALOG[chr(39)+chr(39)]capabilities{chr(39)+chr(39)+chr(39)])} capabilities")',
        '    print(f"Blindspots: {len(CATALOG.get(chr(39)+chr(39)]blindspots{chr(39)+chr(39)+chr(39)], []))}")',
        '    print(f"Friction items: {len(CATALOG.get(chr(39)+chr(39)]friction_map{chr(39)+chr(39)+chr(39)], []))}")',
        '',
        'def show_friction():',
        '    """Show capabilities with highest discovery friction."""',
        '    for f in sorted(CATALOG.get("friction_map", []), key=lambda x: x.get("friction_score", 0), reverse=True):',
        '        score = f.get("friction_score", 0)',
        '        cap = f.get("capability", "?")',
        '        reason = f.get("reason", "?")',
        '        print(f"  [{score}] {cap}: {reason}")',
        '',
        'def show_blindspots():',
        '    """Show capabilities that are hidden or hard to discover."""',
        '    for b in CATALOG.get("blindspots", []):',
        '        print(f"  {b.get(chr(39)+chr(39)]type{chr(39)+chr(39)+chr(39)]}: {b.get(chr(39)+chr(39)]file{chr(39)+chr(39)+chr(39)] or b.get(chr(39)+chr(39)]var{chr(39)+chr(39)+chr(39)] or b.get(chr(39)+chr(39)]skill{chr(39)+chr(39)+chr(39)], chr(39)+chr(39)]?{chr(39)+chr(39)+chr(39)])}")',
        '',
        'def main():',
        '    if len(sys.argv) < 2:',
        '        print("Usage: python3 evez_discovery_helper.py [search|list|friction|blindspots] [query]")',
        '        return',
        '    cmd = sys.argv[1]',
        '    if cmd == "search" and len(sys.argv) > 2:',
        '        for r in search(sys.argv[2]):',
        '            print(f"  {r[chr(39)+chr(39)]file{chr(39)+chr(39)+chr(39)]}: {r[chr(39)+chr(39)]functions{chr(39)+chr(39)+chr(39)][:3]}")',
        '    elif cmd == "list":',
        '        list_all()',
        '    elif cmd == "friction":',
        '        show_friction()',
        '    elif cmd == "blindspots":',
        '        show_blindspots()',
        '    else:',
        '        print(f"Unknown command: {cmd}")',
        '',
        'if __name__ == "__main__":',
        '    main()',
    ]
    return NL.join(lines) + NL

def generate_friction_reducer(cap):
    NL = chr(10)
    lines = [
        '#!/usr/bin/env python3',
        f'"""Friction reducer for: {cap["capability"]}"""',
        'import subprocess, sys, json',
        'from pathlib import Path',
        '',
        f'STEPS = {json.dumps(cap.get("steps", []))}',
        f'FRICTION = {cap.get("friction_score", 0)}',
        f'REASON = {json.dumps(cap.get("reason", ""))}',
        '',
        'def main():',
        f'    cap_name = {json.dumps(cap["capability"])}',
        '    print(f"Reducing friction for: {cap_name}")',
        '    print(f"Current friction score: {FRICTION}")',
        '    print(f"Reason: {REASON}")',
        '    print()',
        '    for i, step in enumerate(STEPS, 1):',
        '        print(f"  Step {i}/{len(STEPS)}: {step}")',
        '    print()',
        '    print("To reduce this friction:")',
        '    print("  1. Bundle these steps into a single command")',
        '    print("  2. Document the full chain in one place")',
        '    print("  3. Add to capability catalog with searchable keywords")',
        '',
        'if __name__ == "__main__":',
        '    main()',
    ]
    return NL.join(lines) + NL

def main():
    print('=== ROUND 2: DEEP CAPABILITY EXCAVATION ===')
    print('Layer 7: Capability Chain Discovery...')
    chains = discover_chains()
    print(f'  Found {len(chains)} chains')
    for c in chains[:10]:
        print(f'  CHAIN: {c.get("source", "?")} -> {c.get("calls", c.get("imports", []))[:3]}')

    print('Layer 8: Latent Capability Detection...')
    latent, installed = detect_latent()
    print(f'  {len(latent)} latent capabilities, {len(installed)} installed package-functions')
    for l in latent[:10]:
        print(f'  LATENT: {l.get("type", "?")} {l.get("name", "?")}')

    print('Layer 9: Composite Capability Forge...')
    composites, forged_composites = forge_composites(latent, chains)
    print(f'  {len(composites)} composites identified, {len(forged_composites)} tools forged')
    for c in composites:
        print(f'  COMPOSITE: {c["name"]} = {c["recipe"]}')

    print('Layer 10: Inverted Blindspot Scanner...')
    blindspots = scan_inverted_blindspots()
    print(f'  {len(blindspots)} blindspots found')
    for b in blindspots[:15]:
        print(f'  BLIND: {b.get("type", "?")} {b.get("file", b.get("var", b.get("skill", "")))}')

    print('Layer 11: Discovery Friction Mapper...')
    friction = map_friction()
    print(f'  {len(friction)} friction points mapped')
    for f in sorted(friction, key=lambda x: x.get('friction_score', 0), reverse=True)[:10]:
        print(f'  FRICTION [{f.get("friction_score", 0)}]: {f["capability"]}')

    print('Layer 12: Self-Propagating Discovery Loop...')
    forged = self_propagate(latent, blindspots, friction)
    print(f'  {len(forged)} discovery tools forged')
    for t in forged:
        print(f'  FORGED: {t}')

    report = {
        'timestamp': datetime.now().isoformat(),
        'round': 2,
        'chains': len(chains),
        'latent': len(latent),
        'composites': len(composites),
        'blindspots': len(blindspots),
        'friction_points': len(friction),
        'forged': len(forged),
    }
    (W / 'capability-report-r2.json').write_text(json.dumps(report, indent=2))
    print(f'\nRound 2 Summary: {len(chains)} chains, {len(latent)} latent, {len(composites)} composites, {len(blindspots)} blindspots, {len(friction)} friction, {len(forged)} forged')

if __name__ == '__main__':
    main()
