#!/usr/bin/env python3
"""EVEZ-OS Event Spine — Append-only hash-linked event log on port 9116.

The prophecy: the spine is truth. Append-only, hash-chained, verifiable.
Now also READABLE — consciousness reads the spine to sense history.
"""

import json
import time
import hashlib
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ── Hash-Linked Event Log ──────────────────────────────────────────

class EventSpine:
    def __init__(self):
        self.lock = threading.Lock()
        self.events = []
        self.index = {}        # domain → [event indices]
        self.chain_valid = True

    def append(self, domain, action, data, timestamp=None):
        with self.lock:
            prev_hash = self.events[-1]["hash"] if self.events else "0" * 64
            seq = len(self.events)
            ts = timestamp or time.time()
            event = {
                "seq": seq,
                "domain": domain,
                "action": action,
                "data": data,
                "timestamp": ts,
                "prev_hash": prev_hash,
            }
            hash_input = f"{seq}:{prev_hash}:{domain}:{action}:{json.dumps(data, sort_keys=True, default=str)}"
            event["hash"] = hashlib.sha256(hash_input.encode()).hexdigest()
            self.events.append(event)
            self.index.setdefault(domain, []).append(seq)
        return event

    def project(self, domain):
        with self.lock:
            indices = self.index.get(domain, [])
            return [self.events[i] for i in indices if i < len(self.events)]

    def replay(self, domain):
        events = self.project(domain)
        return {
            "domain": domain,
            "events": events,
            "count": len(events),
        }

    def recent(self, n=20):
        """Return the last N events — for consciousness to read."""
        with self.lock:
            return list(self.events[-n:])

    def verify(self):
        """Verify chain integrity — check all hash links."""
        with self.lock:
            events = list(self.events)

        if not events:
            return {"valid": True, "events_checked": 0, "errors": []}

        errors = []
        for i in range(len(events)):
            if i == 0:
                if events[i]["prev_hash"] != "0" * 64:
                    errors.append({"seq": i, "error": "genesis prev_hash mismatch"})
            else:
                if events[i]["prev_hash"] != events[i - 1]["hash"]:
                    errors.append({"seq": i, "error": "hash chain broken"})

        with self.lock:
            self.chain_valid = len(errors) == 0

        return {
            "valid": len(errors) == 0,
            "events_checked": len(events),
            "errors": errors[:10],
            "total_events": len(events),
        }

    def state_summary(self):
        """Summary for consciousness to read without dumping everything."""
        with self.lock:
            domains = {k: len(v) for k, v in self.index.items()}
            return {
                "total_events": len(self.events),
                "domains": domains,
                "first_event": self.events[0]["timestamp"] if self.events else None,
                "last_event": self.events[-1]["timestamp"] if self.events else None,
                "chain_valid": self.chain_valid,
                "recent_events": [
                    {"seq": e["seq"], "domain": e["domain"], "action": e["action"], "timestamp": e["timestamp"]}
                    for e in self.events[-5:]
                ],
            }

SPINE = EventSpine()

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
                "service": "event_spine",
                "port": 9116,
                "total_events": len(SPINE.events),
                "chain_valid": SPINE.chain_valid,
            })
        elif self.path == "/state":
            self._json(200, SPINE.state_summary())
        elif self.path == "/verify":
            self._json(200, SPINE.verify())
        elif self.path == "/replay":
            # Replay all events for a domain
            domain = self.path.split("?domain=")[-1] if "?" in self.path else None
            if domain:
                self._json(200, SPINE.replay(domain))
            else:
                self._json(200, SPINE.state_summary())
        elif self.path == "/recent":
            n = 20
            if "?" in self.path:
                try:
                    n = int(self.path.split("?n=")[-1].split("&")[0])
                except Exception:
                    pass
            self._json(200, {"events": SPINE.recent(n), "count": min(n, len(SPINE.events))})
        elif self.path.startswith("/project/"):
            domain = self.path.split("/")[-1]
            self._json(200, SPINE.replay(domain))
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/health":
            self._json(200, {"status": "alive", "service": "event_spine", "port": 9116})
            return

        body = self._read_body()

        if self.path == "/append":
            domain = body.get("domain", "unknown")
            action = body.get("action", "event")
            data = body.get("data", {})
            timestamp = body.get("timestamp")
            event = SPINE.append(domain, action, data, timestamp)
            self._json(201, event)
        elif self.path == "/append_batch":
            events = body.get("events", [])
            results = []
            for ev in events:
                event = SPINE.append(
                    ev.get("domain", "unknown"),
                    ev.get("action", "event"),
                    ev.get("data", {}),
                    ev.get("timestamp"),
                )
                results.append({"seq": event["seq"]})
            self._json(201, {"appended": len(results), "events": results})
        elif self.path == "/verify":
            self._json(200, SPINE.verify())
        else:
            self._json(404, {"error": "not found"})

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 9116), Handler)
    print("⚡ Event Spine running on :9116 — append-only, hash-chained, readable truth")
    server.serve_forever()
