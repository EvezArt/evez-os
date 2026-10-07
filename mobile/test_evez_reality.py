# SPDX-License-Identifier: MIT
#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULE = ROOT / "evez_reality.py"

with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    snapshot = root / "snapshot.json"
    snapshot.write_text(json.dumps({
        "snapshot_id": "snap:mobile",
        "timestamp": "2026-10-07T20:00:00Z",
        "parent_snapshot": None,
        "entities": [],
        "events": [],
        "parameters": {"style": "minimal"},
    }), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(MODULE), "project", str(snapshot), "IMAGE", "phone"],
        text=True, capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["reproducible"] is True
    assert payload["representation"] == "IMAGE"

print("mobile reality substrate tests: PASS")
