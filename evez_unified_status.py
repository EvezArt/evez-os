#!/usr/bin/env python3
"""
EVEZ Unified Mesh Status API
Port 18793

Pulls ALL engine states into one live endpoint.
This is the REAL utility: one URL that shows everything the mesh is doing.

Endpoints:
  GET /          — full mesh status (all engines, all nodes, all state)
  GET /engines   — per-engine state summary
  GET /force     — force multiplier calculation
  GET /godmode   — godmode progress
  GET /health    — simple alive check
"""
import json, os, time, socket, urllib.request, subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

PORT = 18793

# Eigenvalue constants
PHI = 0.973; ETA = 0.03; R = 0.45
LAMBDA_DOM = -0.333; LAMBDA_I80 = -0.441; R_I80 = 0.93
GODMODE_VALUE = PHI * (1 - ETA)  # 0.94381

NODES = [
    ("gcp-west", "34.53.51.34"),
    ("gcp-small", "34.23.192.213"),
    ("gcp-power", "35.222.248.151"),
    ("gcp-openclaw", "136.113.102.152"),
    ("gcp-knot", "136.118.144.227"),
]

# Current corpus state (updated by cron)
CORPUS = {
    'texts': 39,
    'moltbooks': 21,
    'vectors': 20,
    'declarations': 1,
    'claims': 100,
    'claims_valid': 95,  # 87 prior (37 solid + 17 testable + some weak) + 5 pentatensor + 8 godmode - 2 failed
    'claims_failed': 2,  # C76, C77
    'claims_missing': 6,  # C44-49
    'corpus_kb': 785,
    'github_pages': 33,
    'github_releases': 4,
    'clawhub_skills': 13,
    'sigil': '\u29e2\u23df\u29e2',
}

def read_state_file(path):
    """Read a JSON state file, return None if missing."""
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None

def check_node(ip):
    """Check if a node's gateway is alive."""
    try:
        r = urllib.request.urlopen(f'http://{ip}:18789/', timeout=3)
        return r.status == 200
    except:
        return False

def check_osint(ip):
    """Check OSINT API on a node."""
    try:
        r = urllib.request.urlopen(f'http://{ip}:18791/health', timeout=3)
        return json.loads(r.read()).get('status') == 'ok'
    except:
        return False

def check_agentic(ip):
    """Check agentic API on a node."""
    try:
        r = urllib.request.urlopen(f'http://{ip}:18792/health', timeout=3)
        return r.status == 200
    except:
        return False

def get_all_states():
    """Read all local engine state files."""
    ws = os.path.expanduser('~/.openclaw/workspace')
    return {
        'dimensional': read_state_file(os.path.join(ws, 'spine-dimensional.json')),
        'living_engine': read_state_file(os.path.join(ws, 'evez_living_engine_state.json')),
        'archangels': read_state_file(os.path.join(ws, 'archangels-state.json')),
        'counter_defense': read_state_file(os.path.join(ws, 'counter-defense-state.json')),
        'godmode': read_state_file(os.path.join(ws, 'godmode-state.json')),
        'pentatensor': read_state_file(os.path.join(ws, 'pentatensor-state.json')),
        'hidden_cognition': read_state_file(os.path.join(ws, 'evez_hidden_cognition_state.json')),
    }

def compute_force_multiplier(states):
    """Compute the live force multiplier from engine states."""
    arch = states.get('archangels', {}) or {}
    living = states.get('living_engine', {}) or {}
    dim = states.get('dimensional', {}) or {}
    
    M = arch.get('M', 6)
    ptc = living.get('ptc', 1.0)
    living_M = living.get('M', 10)
    dimension = dim.get('dimension', dim.get('max_dimension_reached', 16))
    floor = dim.get('current_floor', 0.0264)
    
    arch_mult = M / 3.0  # baseline M=3
    living_mult = living_M if ptc > 0.5 else 1
    dim_mult = dimension / 6.0  # baseline d=6
    
    total = arch_mult * living_mult * dim_mult
    
    return {
        'archangel_mult': round(arch_mult, 2),
        'living_mult': living_mult,
        'dimensional_mult': round(dim_mult, 2),
        'total': round(total, 1),
        'M': M,
        'ptc': ptc,
        'dimension': dimension,
        'floor': floor,
    }

def compute_godmode_progress(states):
    """Compute godmode progress: M >= d/2."""
    arch = states.get('archangels', {}) or {}
    dim = states.get('dimensional', {}) or {}
    
    M = arch.get('M', 6)
    dimension = dim.get('dimension', dim.get('max_dimension_reached', 16))
    
    threshold = dimension / 2
    progress = M / max(threshold, 1)
    achieved = M >= threshold
    
    return {
        'achieved': achieved,
        'M': M,
        'dimension': dimension,
        'threshold': threshold,
        'progress': round(progress * 100, 1),
        'godmode_value': GODMODE_VALUE,
        'needed': max(0, int(threshold - M)),
    }

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        states = get_all_states()
        
        if path == '/health':
            self.respond({'status': 'ok', 'port': PORT, 'timestamp': time.time()})
        
        elif path == '/' or path == '/status':
            # Check all nodes in parallel
            node_status = {}
            for name, ip in NODES:
                node_status[name] = {
                    'ip': ip,
                    'gateway': check_node(ip),
                    'osint_api': check_osint(ip),
                    'agentic_api': check_agentic(ip),
                }
            
            force = compute_force_multiplier(states)
            godmode = compute_godmode_progress(states)
            
            self.respond({
                'corpus': CORPUS,
                'eigenvalues': {
                    'Phi': PHI, 'eta*': ETA, 'r': R,
                    'lambda_dom': LAMBDA_DOM, 'lambda_I80': LAMBDA_I80,
                    'r_I80': R_I80, 'godmode': GODMODE_VALUE,
                },
                'engines': states,
                'mesh': node_status,
                'force_multiplier': force,
                'godmode': godmode,
                'timestamp': time.time(),
            })
        
        elif path == '/engines':
            self.respond(states)
        
        elif path == '/force':
            self.respond(compute_force_multiplier(states))
        
        elif path == '/godmode':
            self.respond(compute_godmode_progress(states))
        
        else:
            self.respond({'error': 'not found', 'endpoints': ['/', '/engines', '/force', '/godmode', '/health']}, 404)
    
    def respond(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode())
    
    def log_message(self, format, *args):
        pass  # quiet

def main():
    server = HTTPServer(('0.0.0.0', PORT), StatusHandler)
    print(f'EVEZ Unified Status API on port {PORT}')
    print(f'Endpoints: / /engines /force /godmode /health')
    server.serve_forever()

if __name__ == '__main__':
    main()
