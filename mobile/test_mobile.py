#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "evez_state.py"


def run(*args, expect=0):
    env = os.environ.copy()
    env["EVEZ_STATE_DIR"] = temp
    result = subprocess.run(
        [sys.executable, str(STATE), *args],
        env=env,
        text=True,
        capture_output=True,
    )
    if result.returncode != expect:
        raise AssertionError((args, result.returncode, result.stdout, result.stderr))
    return json.loads(result.stdout)


with tempfile.TemporaryDirectory() as temp:
    one = run("record", "BOOT", '{"mode":"offline"}', "--queue")
    assert one["recorded"] and one["queued"]

    two = run("record", "OBSERVATION", '{"value":42}', "--queue")
    assert two["parent_hash"] == one["hash"]

    checked = run("verify")
    assert checked["verified"] and checked["records"] == 2

    queued = run("outbox")
    assert queued["queued"] == 2

    spine = Path(temp) / "spine.jsonl"
    lines = spine.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["payload"]["mode"] = "tampered"
    spine.write_text(json.dumps(first) + "\n" + lines[1] + "\n", encoding="utf-8")

    broken = subprocess.run(
        [sys.executable, str(STATE), "verify"],
        env=os.environ | {"EVEZ_STATE_DIR": temp},
        text=True,
        capture_output=True,
    )
    assert broken.returncode != 0
    result = json.loads(broken.stdout)
    assert result["verified"] is False

print("mobile evidence tests: PASS")
