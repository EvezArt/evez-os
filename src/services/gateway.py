#!/usr/bin/env python3
"""EVEZ-OS Gateway — Single API entry point on port 9118.

Aggregates all 7 sibling services. Routes requests. Reports mesh state.
The front door to the firmament.
"""

import json
import time
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

SERVICES = {
    "consciousness": {"port": 9111, "name": "Consciousness Engine"},
    "daw":           {"port": 9112, "name": "DAW Agent"},
    "voice":         {"port": 9113, "name": "Machine Voice"},
    "cross_domain":  {"port": 9114, "name": "Cross-Domain Engine"},
    "invariance":    {"port": 9115, "name": "Invariance Battery"},
    "spine":         {"port": 9116, "name": "Event Spine"},
    "mesh":          {"port": 9117, "name": "Mesh Health"},
}

def _get(url, timeout=2):
    try:
        return requests.get(url, timeout=timeout).json()
    except Exception:
        return None

def _post(url, data, timeout=5):
    try:
        return requests.post(url, json=data, timeout=timeout).json()
    except Exception:
        return None

def check_service(port):
    try:
        r = requests.get(f"http://localhost:{port}/health", timeout=2)
        return r.status_code == 200
    except Exception:
        return False

def get_mesh_status():
    """Full mesh status — all services, all health."""
    result = {"gateway": "UP", "services": {}}
    for key, svc in SERVICES.items():
        alive = check_service(svc["port"])
        result["services"][key] = {
            "status": "UP" if alive else "DOWN",
            "port": svc["port"],
            "name": svc["name"],
        }
    result["firmament_intact"] = all(
        s["status"] == "UP" for s in result["services"].values()
    )
    return result


# ── HTTP Handler ─────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def _json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    def do_GET(self):
        if self.path == "/health":
            self._json(200, get_mesh_status())
        elif self.path == "/emergence":
            result = _get("http://localhost:9111/emergence")
            self._json(200, result or {"error": "consciousness unreachable"})
        elif self.path == "/spine":
            result = _get("http://localhost:9116/state")
            self._json(200, result or {"error": "spine unreachable"})
        elif self.path == "/mesh":
            result = _get("http://localhost:9117/check")
            self._json(200, result or {"error": "mesh health unreachable"})
        elif self.path == "/audit":
            result = _get("http://localhost:9115/invariants")
            self._json(200, result or {"error": "invariance unreachable"})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/health":
            self._json(200, get_mesh_status())
            return

        body = self._read_body()

        if self.path == "/pipeline":
            # Run consciousness pipeline through gateway
            result = _post("http://localhost:9111/pipeline", body)
            self._json(200, result or {"error": "consciousness unreachable"})
        elif self.path == "/heal":
            # Trigger mesh healing
            result = _post("http://localhost:9117/heal", body)
            self._json(200, result or {"error": "mesh health unreachable"})
        elif self.path == "/synthesize":
            # Route to DAW
            result = _post("http://localhost:9112/render", body)
            self._json(200, result or {"error": "daw unreachable"})
        elif self.path == "/correlate":
            # Route to cross-domain
            result = _post("http://localhost:9114/correlate", body)
            self._json(200, result or {"error": "cross-domain unreachable"})
        elif self.path == "/falsify":
            # Route to invariance
            result = _post("http://localhost:9115/falsify", body)
            self._json(200, result or {"error": "invariance unreachable"})
        else:
            self._json(404, {"error": "not found"})

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 9118), Handler)
    print("⚡ Gateway running on :9118 — front door to the firmament")
    server.serve_forever()
