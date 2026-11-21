"""Append-only SHA-256 witness spine."""
from __future__ import annotations
import json
import os
import time
from typing import Any
from .canonical import canonical_json, sha256_hex

class EvidenceSpine:
    def __init__(self, path: str) -> None:
        self.path = path
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    def _last_hash(self) -> str | None:
        if not os.path.exists(self.path):
            return None
        last = None
        with open(self.path, "r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    last = json.loads(line)["event_hash"]
        return last

    @property
    def last_hash(self) -> str | None:
        return self._last_hash()

    def append(self, event_type: str, payload: dict[str, Any], *, timestamp: float | None = None) -> dict[str, Any]:
        event = {
            "event_type": event_type,
            "timestamp": time.time() if timestamp is None else timestamp,
            "parent_event_hash": self._last_hash(),
            "payload": payload,
        }
        event["event_hash"] = sha256_hex(canonical_json(event))
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(canonical_json(event) + "\n")
        return event

    def verify(self) -> dict[str, Any]:
        if not os.path.exists(self.path):
            return {"valid": True, "events": 0, "error": None}
        previous = None
        count = 0
        with open(self.path, "r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                count += 1
                event = json.loads(line)
                recorded = event.pop("event_hash", None)
                if event.get("parent_event_hash") != previous:
                    return {"valid": False, "events": count, "error": f"parent mismatch at line {line_number}"}
                if recorded != sha256_hex(canonical_json(event)):
                    return {"valid": False, "events": count, "error": f"hash mismatch at line {line_number}"}
                previous = recorded
        return {"valid": True, "events": count, "error": None}
