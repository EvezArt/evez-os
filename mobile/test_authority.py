#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "mobile" / "evez_authority.py"

def run(args, env, input_text="test-pass\n"):
    result = subprocess.run(
        [sys.executable, str(AUTH), *args],
        text=True,
        input=input_text,
        capture_output=True,
        env=env,
    )
    if result.returncode != 0:
        raise AssertionError((args, result.stdout, result.stderr))
    return json.loads(result.stdout)

with tempfile.TemporaryDirectory() as temp:
    env = os.environ.copy()
    env["EVEZ_AUTHORITY_DIR"] = temp

    run(["init-role", "operator"], env, "test-pass\ntest-pass\n")
    run(["init-role", "reviewer"], env, "test-pass\ntest-pass\n")

    one = run(
        ["sign", "operator", "DEPLOY", '{"commit":"abc123"}', "--operation-id", "op-001"],
        env,
    )
    two = run(
        ["sign", "reviewer", "DEPLOY", '{"commit":"abc123"}', "--operation-id", "op-001"],
        env,
    )

    approved = run(
        ["quorum", one["saved_to"], two["saved_to"],
         str(Path(temp) / "operator-public.pem"),
         str(Path(temp) / "reviewer-public.pem")],
        env,
        "",
    )
    assert approved["approved"] is True

    advanced = run(["advance-epoch"], env, "")
    assert advanced["epoch"] == 2

    stale = subprocess.run(
        [sys.executable, str(AUTH), "quorum", one["saved_to"], two["saved_to"],
         str(Path(temp) / "operator-public.pem"),
         str(Path(temp) / "reviewer-public.pem")],
        text=True,
        capture_output=True,
        env=env,
    )
    assert stale.returncode != 0
    assert "epoch" in stale.stdout.lower()

    bg = run(["break-glass", "READ_STATUS", "operator recovery drill"], env, "")
    assert bg["recorded"] is True

print("command authority dual-control test: PASS")
