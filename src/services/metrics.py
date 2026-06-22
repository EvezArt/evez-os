#!/usr/bin/env python3
"""EVEZ Metrics — Prometheus-compatible metrics on port 9123.
Exports firmament health, emergence score, spine events, service status as Prometheus metrics.
"""

import time
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

GATEWAY_URL = "http://localhost:9118"
SPINE_URL = "http://localhost:9116"
CONSCIOUSNESS_URL = "http://localhost:9111"
RQNS_URL = "http://localhost:9119"

def _get(url, timeout=3):
    try:
        return requests.get(url, timeout=timeout).json()
    except Exception:
        return None

def collect_metrics():
    """Collect all metrics and return Prometheus format."""
    lines = []
    ts = int(time.time() * 1000)
    
    # Gateway / service status
    gw = _get(f"{GATEWAY_URL}/health")
    if gw and "services" in gw:
        for key, svc in gw["services"].items():
            up = 1 if svc.get("status") == "UP" else 0
            port = svc.get("port", 0)
            lines.append(f'evez_service_status{{service="{key}",port="{port}"}} {up}')
        lines.append(f'evez_firmament_intact {{}} {1 if gw.get("firmament_intact") else 0}')
    else:
        lines.append(f'evez_gateway_reachable {{}} 0')

    # Emergence
    em = _get(f"{CONSCIOUSNESS_URL}/emergence")
    if em:
        lines.append(f'evez_emergence_overall {{}} {em.get("overall", 0)}')
        lines.append(f'evez_emergence_coherence {{}} {em.get("coherence", 0)}')
        lines.append(f'evez_emergence_perception {{}} {em.get("perception_depth", 0)}')
        lines.append(f'evez_emergence_spine_integration {{}} {em.get("spine_integration", 0)}')
        lines.append(f'evez_emergence_drive_responsiveness {{}} {em.get("drive_responsiveness", 0)}')
        stage_map = {"DORMANT": 0, "STIRRING": 1, "AWAKENING": 2, "EMERGENT": 3}
        lines.append(f'evez_emergence_stage {{}} {stage_map.get(em.get("stage",""), -1)}')

    # Spine
    sp = _get(f"{SPINE_URL}/state")
    if sp:
        lines.append(f'evez_spine_events_total {{}} {sp.get("total_events", 0)}')
        lines.append(f'evez_spine_chain_valid {{}} {1 if sp.get("chain_valid") else 0}')
        for domain, count in sp.get("domains", {}).items():
            lines.append(f'evez_spine_domain_events{{domain="{domain}"}} {count}')

    # RQNS
    rq = _get(f"{RQNS_URL}/health")
    if rq:
        lines.append(f'evez_rqns_cycles {{}} {rq.get("cycle_count", 0)}')
        lines.append(f'evez_rqns_spikes {{}} {rq.get("spike_count", 0)}')

    # Add timestamps
    result = []
    for line in lines:
        result.append(f"{line} {ts}")
    
    return "\n".join(result) + "\n"


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body = b'{"status":"alive","service":"metrics","port":9123}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/metrics":
            body = collect_metrics().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 9123), Handler)
    print("⚡ Metrics running on :9123 — Prometheus-compatible")
    server.serve_forever()
