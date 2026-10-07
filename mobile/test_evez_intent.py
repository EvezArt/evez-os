#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULE = ROOT / "evez_intent.py"

with tempfile.TemporaryDirectory() as temp:
    path = Path(temp) / "candidates.json"
    path.write_text(json.dumps([
        "verify the release artifact against the published checksum",
        "do it",
    ]), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(MODULE), "--file", str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2, (result.stdout, result.stderr)
    payload = json.loads(result.stdout)
    assert payload["status"] == "REQUIRES_SPECIFICATION"
    assert payload["candidate_count"] == 2

print("mobile intent optimizer tests: PASS")
