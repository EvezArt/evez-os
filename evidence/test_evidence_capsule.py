#!/usr/bin/env python3
from __future__ import annotations
import tempfile
from pathlib import Path
from evidence_capsule import build, verify

with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    first = root / "first.json"
    second = root / "notes.txt"
    first.write_text('{"claim":"UNKNOWN","truth":null}\n', encoding="utf-8")
    second.write_text("sensor note\n", encoding="utf-8")
    capsule = build([("claim", str(first)), ("notes", str(second))], {"purpose": "unit-test"})
    checked = verify(capsule)
    assert checked["verified"] is True
    assert checked["artifact_count"] == 2
    assert len(capsule["capsule_sha256"]) == 64
    capsule["artifacts"][0]["content"] = '{"claim":"FALSE","truth":true}\n'
    broken = verify(capsule)
    assert broken["verified"] is False
    assert any(row["error"] == "artifact_hash_mismatch" for row in broken["errors"])
print("evidence capsule test: PASS")
