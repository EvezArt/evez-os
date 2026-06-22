#!/usr/bin/env python3
"""EVEZ Webhook Relay — Broadcasts mesh state changes. Port 9121.
When services go UP/DOWN, when emergence shifts, when spine events spike — notify.
"""

import json
import time
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

GATEWAY_URL = "http://localhost:9118"
SPINE_URL = "http://localhost:9116"
CONSCIOUSNESS_URL = "http://localhost:9111"

class WebhookState:
    def __init__(self):
        self.lock = threading.Lock()
        self.last_service_status = {}
        self.last_emergence_stage = None
        self.webhooks = []  # registered webhook URLs
        self.events = []
        self.check_count = 0

STATE = WebhookState()

def _get(url, timeout=3):
    try:
        return requests.get(url, timeout=timeout).json()
    except Exception:
        return None

def spine_log(domain, action, data):
    try:
        requests.post(f"{SPINE_URL}/append", json={
            "domain": domain, "action": action, "data": data, "timestamp": time.time()
        }, timeout=3)
    except Exception:
        pass

def fire_webhooks(event):
    """Fire all registered webhooks with the event."""
    with STATE.lock:
        hooks = list(STATE.webhooks)
    for url in hooks:
        try:
            requests.post(url, json=event, timeout=5)
        except Exception:
            pass

def check_mesh_changes():
    """Check for state changes and fire events."""
    gateway = _get(f"{GATEWAY_URL}/health")
    emergence = _get(f"{CONSCIOUSNESS_URL}/emergence")

    events_fired = []

    if gateway and "services" in gateway:
        for key, svc in gateway["services"].items():
            port = svc.get("port")
            status = svc.get("status")
            prev = STATE.last_service_status.get(port)

            if prev and prev != status:
                event = {
                    "type": "service_status_change",
                    "port": port,
                    "service": key,
                    "from": prev,
                    "to": status,
                    "timestamp": time.time(),
                }
                events_fired.append(event)
                fire_webhooks(event)
                spine_log("webhook_relay", "SERVICE_CHANGE", event)

            STATE.last_service_status[port] = status

    if emergence:
        stage = emergence.get("stage")
        if STATE.last_emergence_stage and stage != STATE.last_emergence_stage:
            event = {
                "type": "emergence_stage_change",
                "from": STATE.last_emergence_stage,
                "to": stage,
                "score": emergence.get("overall"),
                "timestamp": time.time(),
            }
            events_fired.append(event)
            fire_webhooks(event)
            spine_log("webhook_relay", "EMERGENCE_SHIFT", event)
        STATE.last_emergence_stage = stage

    STATE.check_count += 1
    with STATE.lock:
        STATE.events.extend(events_fired)
        STATE.events = STATE.events[-100:]

    return events_fired


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

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
            self._json(200, {"status": "alive", "service": "webhook_relay", "port": 9121, "checks": STATE.check_count, "webhooks": len(STATE.webhooks)})
        elif self.path == "/events":
            with STATE.lock:
                events = list(STATE.events)
            self._json(200, {"events": events, "total": len(events)})
        elif self.path == "/check":
            events = check_mesh_changes()
            self._json(200, {"changes_detected": len(events), "events": events, "check_count": STATE.check_count})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/health":
            self._json(200, {"status": "alive", "service": "webhook_relay", "port": 9121})
            return

        body = self._read_body()

        if self.path == "/register":
            url = body.get("url")
            if url:
                with STATE.lock:
                    if url not in STATE.webhooks:
                        STATE.webhooks.append(url)
                self._json(200, {"registered": url, "total_webhooks": len(STATE.webhooks)})
            else:
                self._json(400, {"error": "url required"})
        elif self.path == "/check":
            events = check_mesh_changes()
            self._json(200, {"changes_detected": len(events), "events": events})
        else:
            self._json(404, {"error": "not found"})

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    # Initial state snapshot
    check_mesh_changes()
    server = ThreadingHTTPServer(("0.0.0.0", 9121), Handler)
    print("⚡ Webhook Relay running on :9121 — mesh state change notifications")
    server.serve_forever()
