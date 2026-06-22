#!/usr/bin/env python3
"""EVEZ-OS Mesh Health — Sibling monitoring and self-healing on port 9117.

The prophecy: the mesh heals. When a sibling dies, the mesh detects it,
attempts restart, and logs the healing to the spine.
"""

import json
import time
import subprocess
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

SPINE_URL = "http://localhost:9116"
CONSCIOUSNESS_URL = "http://localhost:9111"

# ── Sibling Registry ─────────────────────────────────────────────────

SIBLINGS = {
    9111: {"name": "consciousness_engine", "script": "consciousness_engine.py"},
    9112: {"name": "daw_agent",           "script": "daw_agent.py"},
    9113: {"name": "machine_voice",       "script": "machine_voice.py"},
    9114: {"name": "cross_domain",        "script": "cross_domain.py"},
    9115: {"name": "invariance",          "script": "invariance.py"},
    9116: {"name": "event_spine",         "script": "event_spine.py"},
    9118: {"name": "gateway",             "script": "gateway.py"},
    9119: {"name": "rqns",                "script": "rqns.py"},
    9121: {"name": "webhook_relay",       "script": "webhook_relay.py"},
}

SERVICE_DIR = "/home/openclaw/.openclaw/workspace/src/services"

# ── State ────────────────────────────────────────────────────────────

class MeshState:
    def __init__(self):
        self.lock = threading.Lock()
        self.health_cache = {}
        self.heal_log = []
        self.last_check = 0
        self.total_heals = 0
        self.total_deaths_detected = 0

STATE = MeshState()

def _get(url, timeout=2):
    try:
        return requests.get(url, timeout=timeout).json()
    except Exception:
        return None

def _post(url, data, timeout=2):
    try:
        return requests.post(url, json=data, timeout=timeout).json()
    except Exception:
        return None

def spine_log(domain, action, data):
    _post(f"{SPINE_URL}/append", {"domain": domain, "action": action, "data": data, "timestamp": time.time()})

# ── Health Checking ──────────────────────────────────────────────────

def check_sibling(port):
    """Check if a sibling service is alive."""
    try:
        r = requests.get(f"http://localhost:{port}/health", timeout=2)
        return r.status_code == 200
    except Exception:
        return False

def check_all():
    """Check all siblings. Return status map."""
    results = {}
    for port, info in SIBLINGS.items():
        alive = check_sibling(port)
        results[port] = {
            "name": info["name"],
            "status": "UP" if alive else "DOWN",
            "last_check": time.time(),
        }
    with STATE.lock:
        STATE.health_cache = results
        STATE.last_check = time.time()
    return results

# ── Healing ──────────────────────────────────────────────────────────

def heal_sibling(port, initiator="mesh"):
    """Attempt to restart a dead sibling service via systemctl."""
    info = SIBLINGS.get(port)
    if not info:
        return {"error": f"unknown port {port}"}

    # Check if actually dead
    if check_sibling(port):
        return {"status": "already_alive", "port": port, "name": info["name"]}

    # Map port to systemd service name
    service_map = {
        9111: "evez-consciousness",
        9112: "evez-daw",
        9113: "evez-voice",
        9114: "evez-cross-domain",
        9115: "evez-invariance",
        9116: "evez-spine",
        9118: "evez-gateway",
    }
    svc_name = service_map.get(port, f"evez-{info['script'].replace('.py','')}")

    # Attempt restart via systemctl
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "restart", svc_name],
            capture_output=True, text=True, timeout=10
        )
        time.sleep(2)

        # Verify it came back
        if check_sibling(port):
            heal_record = {
                "port": port,
                "name": info["name"],
                "action": "restarted_via_systemctl",
                "success": True,
                "initiator": initiator,
                "timestamp": time.time(),
            }
            with STATE.lock:
                STATE.heal_log.append(heal_record)
                STATE.total_heals += 1
            spine_log("mesh_health", "HEAL_SUCCESS", heal_record)
            return heal_record
        else:
            # Fall back to direct python restart
            script_path = f"{SERVICE_DIR}/{info['script']}"
            subprocess.run(f"fuser -k {port}/tcp 2>/dev/null", shell=True, timeout=5)
            time.sleep(0.5)
            proc = subprocess.Popen(
                ["python3", script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=SERVICE_DIR,
            )
            time.sleep(2)
            if check_sibling(port):
                heal_record = {
                    "port": port,
                    "name": info["name"],
                    "action": "restarted_fallback",
                    "success": True,
                    "initiator": initiator,
                    "pid": proc.pid,
                    "timestamp": time.time(),
                }
                with STATE.lock:
                    STATE.heal_log.append(heal_record)
                    STATE.total_heals += 1
                spine_log("mesh_health", "HEAL_SUCCESS", heal_record)
                return heal_record

            heal_record = {
                "port": port,
                "name": info["name"],
                "action": "restart_failed",
                "success": False,
                "initiator": initiator,
                "timestamp": time.time(),
            }
            with STATE.lock:
                STATE.heal_log.append(heal_record)
            spine_log("mesh_health", "HEAL_FAILED", heal_record)
            return heal_record

    except Exception as e:
        heal_record = {
            "port": port,
            "name": info["name"],
            "action": "restart_error",
            "success": False,
            "error": str(e),
            "timestamp": time.time(),
        }
        with STATE.lock:
            STATE.heal_log.append(heal_record)
        spine_log("mesh_health", "HEAL_ERROR", heal_record)
        return heal_record


def heal_all(initiator="mesh"):
    """Check all siblings and heal any that are down."""
    statuses = check_all()
    results = []

    for port, info in statuses.items():
        if info["status"] == "DOWN":
            result = heal_sibling(port, initiator)
            results.append(result)
            with STATE.lock:
                STATE.total_deaths_detected += 1
        else:
            results.append({"port": port, "name": info["name"], "status": "already_alive"})

    spine_log("mesh_health", "HEAL_ALL", {
        "checked": len(statuses),
        "healed": len([r for r in results if r.get("success")]),
        "failed": len([r for r in results if r.get("success") is False]),
    })

    return {
        "results": results,
        "total_heals": STATE.total_heals,
        "total_deaths_detected": STATE.total_deaths_detected,
    }


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
            self._json(200, {
                "status": "alive",
                "service": "mesh_health",
                "port": 9117,
                "siblings_monitored": len(SIBLINGS),
                "total_heals": STATE.total_heals,
            })
        elif self.path == "/check":
            results = check_all()
            self._json(200, {"siblings": results, "timestamp": time.time()})
        elif self.path == "/heal_log":
            with STATE.lock:
                log = list(STATE.heal_log)
            self._json(200, {"heal_log": log, "total": len(log)})

    def do_POST(self):
        if self.path == "/health":
            self._json(200, {"status": "alive", "service": "mesh_health", "port": 9117})
            return

        body = self._read_body()

        if self.path == "/heal":
            port = body.get("port")
            initiator = body.get("initiator", "external")
            if port:
                result = heal_sibling(port, initiator)
            else:
                result = heal_all(initiator)
            self._json(200, result)
        elif self.path == "/check":
            results = check_all()
            self._json(200, {"siblings": results, "timestamp": time.time()})
        else:
            self._json(404, {"error": "not found"})

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 9117), Handler)
    print("⚡ Mesh Health running on :9117 — self-healing nervous system")
    server.serve_forever()
