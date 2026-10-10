#!/usr/bin/env python3
"""EVEZ-OS Event Spine — Append-only hash-linked event log on port 9116."""

import json
import copy
import math
import rfc8785
import time
import hashlib
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ── Hash-Linked Event Log ──────────────────────────────────────────

class EventSpine:
    """Append-only event log with versioned, recomputable event hashes.

    v1 hashes preserve the historical formula and are verified for compatibility;
    their timestamp is not covered by that legacy formula. New v2 events hash
    all stored fields except the digest using RFC 8785 canonical JSON, including
    the timestamp.
    """
    def __init__(self):
        self.lock = threading.RLock()
        self._events = []
        self.index = {}
        self.idempotency_index = {}
        self.chain_valid = True

    @property
    def events(self):
        """Return a snapshot so callers cannot mutate stored history by alias."""
        with self.lock:
            return copy.deepcopy(self._events)

    @staticmethod
    def _legacy_hash(event):
        hash_input = (
            f"{event['seq']}:{event['prev_hash']}:{event['domain']}:"
            f"{event['action']}:{json.dumps(event['data'], sort_keys=True, default=str)}"
        )
        return hashlib.sha256(hash_input.encode()).hexdigest()

    @staticmethod
    def _v2_hash(event):
        payload = {key: value for key, value in event.items() if key != "hash"}
        return hashlib.sha256(rfc8785.dumps(payload)).hexdigest()

    @classmethod
    def _compute_hash(cls, event):
        version = event.get("hash_version", 1)
        if type(version) is not int:
            raise ValueError("Event hash version must be an integer")
        if version == 1:
            return cls._legacy_hash(event)
        if version == 2:
            return cls._v2_hash(event)
        raise ValueError(f"Unsupported event hash version: {version}")

    def append(self, domain, action, data, timestamp=None, idempotency_key=None):
        if not isinstance(domain, str) or not domain:
            raise ValueError("domain must be a non-empty string")
        if not isinstance(action, str) or not action:
            raise ValueError("action must be a non-empty string")
        if idempotency_key is not None:
            if not isinstance(idempotency_key, str) or not idempotency_key or len(idempotency_key) > 256:
                raise ValueError("idempotency_key must be a non-empty string up to 256 characters")
        ts = time.time() if timestamp is None else timestamp
        if isinstance(ts, bool) or not isinstance(ts, (int, float)) or not math.isfinite(ts):
            raise ValueError("timestamp must be a finite numeric epoch timestamp")

        # JCS validates the data as interoperable JSON before touching the ledger.
        data_copy = copy.deepcopy(data)
        rfc8785.dumps({"data": data_copy})

        with self.lock:
            if not self.chain_valid:
                raise ValueError("Refusing to append to an invalid event chain")
            if self._events:
                head = self._events[-1]
                expected_previous = self._events[-2]["hash"] if len(self._events) > 1 else "0" * 64
                try:
                    head_ok = (
                        type(head.get("seq")) is int
                        and head.get("seq") == len(self._events) - 1
                        and head.get("prev_hash") == expected_previous
                        and head.get("hash") == self._compute_hash(head)
                    )
                except Exception:
                    head_ok = False
                if not head_ok:
                    self.chain_valid = False
                    raise ValueError("Refusing to append because the current chain head is invalid")

            if idempotency_key is not None:
                existing_seq = self.idempotency_index.get((domain, idempotency_key))
                if existing_seq is not None:
                    integrity = self.verify()
                    if not integrity["valid"]:
                        raise ValueError("Refusing to reuse an idempotency key on an invalid chain")
                    existing = self._events[existing_seq]
                    existing_fingerprint = hashlib.sha256(rfc8785.dumps({
                        "domain": domain, "action": existing["action"], "data": existing["data"]
                    })).hexdigest()
                    new_fingerprint = hashlib.sha256(rfc8785.dumps({
                        "domain": domain, "action": action, "data": data_copy
                    })).hexdigest()
                    if existing_fingerprint != new_fingerprint:
                        raise ValueError("idempotency_key already exists for different event content")
                    return copy.deepcopy(existing)

            prev_hash = self._events[-1]["hash"] if self._events else "0" * 64
            event = {
                "seq": len(self._events),
                "domain": domain,
                "action": action,
                "data": data_copy,
                "timestamp": ts,
                "prev_hash": prev_hash,
                "hash_version": 2,
            }
            if idempotency_key is not None:
                event["idempotency_key"] = idempotency_key
            event["hash"] = self._compute_hash(event)
            self._events.append(event)
            self.index.setdefault(domain, []).append(event["seq"])
            if idempotency_key is not None:
                self.idempotency_index[(domain, idempotency_key)] = event["seq"]
            self.chain_valid = True
            return copy.deepcopy(event)

    def project(self, domain):
        with self.lock:
            indices = self.index.get(domain, [])
            return [copy.deepcopy(self._events[i]) for i in indices
                    if isinstance(i, int) and 0 <= i < len(self._events)]

    def replay(self, domain):
        events = self.project(domain)
        return {"domain": domain, "events": events, "count": len(events)}

    def recent(self, n=20):
        """Return a defensive snapshot of the last N events."""
        if isinstance(n, bool) or not isinstance(n, int):
            raise ValueError("n must be an integer")
        if n < 0:
            raise ValueError("n must be non-negative")
        with self.lock:
            return copy.deepcopy(self._events[-n:] if n else [])

    def verify(self):
        """Recompute each event digest and verify chain order and predecessor links."""
        with self.lock:
            events = copy.deepcopy(self._events)

        errors = []
        warnings = []
        previous = "0" * 64
        for index, event in enumerate(events):
            if not isinstance(event, dict):
                errors.append({"seq": index, "error": "event is not an object"})
                continue
            if type(event.get("seq")) is not int or event.get("seq") != index:
                errors.append({"seq": index, "error": "sequence mismatch"})
            if event.get("prev_hash") != previous:
                errors.append({"seq": index, "error": "hash chain broken"})
            version = event.get("hash_version", 1)
            if version == 1:
                warnings.append({
                    "seq": index,
                    "warning": "legacy v1 hash does not cover timestamp or extra fields",
                })
            try:
                expected = self._compute_hash(event)
            except Exception as exc:
                errors.append({
                    "seq": index,
                    "error": f"event hash recomputation failed: {type(exc).__name__}",
                })
            else:
                if event.get("hash") != expected:
                    errors.append({"seq": index, "error": "event content hash mismatch"})
            recorded_hash = event.get("hash")
            if isinstance(recorded_hash, str) and len(recorded_hash) == 64:
                previous = recorded_hash
            else:
                errors.append({"seq": index, "error": "invalid event hash format"})
                previous = "0" * 64

        valid = len(errors) == 0
        with self.lock:
            self.chain_valid = valid
        return {
            "valid": valid,
            "events_checked": len(events),
            "errors": errors[:10],
            "total_events": len(events),
            "warnings": warnings[:10],
            "total_warnings": len(warnings),
        }

    def state_summary(self):
        """Summary view; it does not expose mutable references to the ledger."""
        with self.lock:
            domains = {key: len(value) for key, value in self.index.items()}
            events = self._events
            return {
                "total_events": len(events),
                "domains": domains,
                "first_event": events[0]["timestamp"] if events else None,
                "last_event": events[-1]["timestamp"] if events else None,
                "chain_valid": self.chain_valid,
                "recent_events": [
                    {"seq": e["seq"], "domain": e["domain"], "action": e["action"], "timestamp": e["timestamp"]}
                    for e in events[-5:]
                ],
            }

SPINE = EventSpine()

# ── HTTP Handler ─────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def _json(self, code, data):
        body = json.dumps(data, default=str).encode()
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
            self._json(200, {"status": "alive", "service": "event_spine", "port": 9116})
        elif self.path == "/status":
            self._json(200, SPINE.stats())
        elif self.path == "/verify":
            self._json(200, SPINE.verify())
        elif self.path.startswith("/project/"):
            domain = self.path.split("/project/", 1)[1]
            self._json(200, {"domain": domain, "events": SPINE.project(domain)})
        elif self.path.startswith("/replay/"):
            domain = self.path.split("/replay/", 1)[1]
            self._json(200, SPINE.replay(domain))
        elif self.path == "/events":
            # Last 50 events
            with SPINE.lock:
                events = SPINE.events[-50:]
            self._json(200, {"events": events, "showing": len(events)})
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
            event = SPINE.append(domain, action, data, timestamp, body.get("idempotency_key"))
            self._json(201, event)
        elif self.path == "/project":
            domain = body.get("domain", "")
            if not domain:
                self._json(400, {"error": "domain required"})
                return
            self._json(200, {"domain": domain, "events": SPINE.project(domain)})
        elif self.path == "/replay":
            domain = body.get("domain", "")
            if not domain:
                self._json(400, {"error": "domain required"})
                return
            self._json(200, SPINE.replay(domain))
        elif self.path == "/verify":
            self._json(200, SPINE.verify())
        else:
            self._json(404, {"error": "not found"})

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 9116), Handler)
    print("Event Spine running on :9116")
    server.serve_forever()
