#!/usr/bin/env python3
"""Recursive tool forge - discovers missing Python packages and generates install/verify scripts."""
import importlib, subprocess, sys
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')
F = W / 'tool-forge'
F.mkdir(exist_ok=True)

CAPS = {
    'matplotlib': 'data_viz',
    'pandas': 'data_analysis',
    'aiohttp': 'async_http',
    'websockets': 'ws_server',
    'PIL': 'image_proc',
    'psycopg2': 'postgres',
    'redis': 'cache',
    'docker': 'containers',
}

def discover():
    g = []
    for pkg, cap in CAPS.items():
        try:
            importlib.import_module(pkg)
        except ImportError:
            g.append((pkg, cap))
    return g

def main():
    gs = discover()
    if not gs:
        print('No gaps found.')
        return
    print(f'Found {len(gs)} gaps')
    for pkg, cap in gs:
        fn = 'forge_' + cap + '.py'
        lines = [
            '#!/usr/bin/env python3',
            'import subprocess, sys',
            'if "--install" in sys.argv:',
            '    subprocess.run(["pip3", "install", "--break-system-packages", "' + pkg + '"])',
            'elif "--verify" in sys.argv:',
            '    try:',
            '        __import__("' + pkg.replace('-', '_') + '"); print("INSTALLED")',
            '    except: print("MISSING")',
        ]
        (F / fn).write_text(chr(10).join(lines) + chr(10))
        print(f'Forged: {fn}')
    print(f'{len(gs)} tools in {F}/')

if __name__ == '__main__':
    main()
