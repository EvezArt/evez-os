#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IDENTITY = ROOT.parent / "identity" / "evez.identity.json"
MODULE = ROOT / "evez_identity.py"
CTL = ROOT / "evezctl"

with tempfile.TemporaryDirectory() as temp:
    temp_root = Path(temp)
    identity_copy = temp_root / "identity.json"
    identity_copy.write_bytes(IDENTITY.read_bytes())
    state_dir = temp_root / "state"
    env = os.environ.copy()
    env.update(
        {
            "EVEZ_IDENTITY_FILE": str(identity_copy),
            "EVEZ_STATE_DIR": str(state_dir),
            "EVEZ_ROOT": str(ROOT.parent),
            "EVEZ_CONFIG": str(temp_root / "missing.env"),
            "EVEZ_LOG_DIR": str(temp_root / "logs"),
            "HOME": str(temp_root),
        }
    )

    verified = subprocess.run(
        [sys.executable, str(MODULE), "verify"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert verified.returncode == 0, (verified.stdout, verified.stderr)
    verified_payload = json.loads(verified.stdout)
    assert verified_payload["verified"] is True
    assert len(verified_payload["sha256"]) == 64

    shown = subprocess.run(
        [sys.executable, str(MODULE), "show"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert shown.returncode == 0, (shown.stdout, shown.stderr)
    snapshot = json.loads(shown.stdout)
    assert snapshot["identity"]["verified"] is True
    assert snapshot["identity"]["name"] == "EVEZ"
    assert snapshot["authority"]["default"] == "NONE"

    witnessed = subprocess.run(
        [sys.executable, str(MODULE), "self-witness"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert witnessed.returncode == 0, (witnessed.stdout, witnessed.stderr)
    witness_payload = json.loads(witnessed.stdout)
    assert witness_payload["recorded"] is True

    spine = state_dir / "spine.jsonl"
    rows = [json.loads(line) for line in spine.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    assert rows[0]["type"] == "IDENTITY_SELF_WITNESS"
    assert rows[0]["payload"]["identity_sha256"] == verified_payload["sha256"]

    tampered = temp_root / "tampered.json"
    shutil.copyfile(identity_copy, tampered)
    value = json.loads(tampered.read_text(encoding="utf-8"))
    value["identity"]["name"] = "NOT-EVEZ"
    tampered.write_text(json.dumps(value), encoding="utf-8")

    invalid = subprocess.run(
        [sys.executable, str(MODULE), "verify"],
        env=env | {"EVEZ_IDENTITY_FILE": str(tampered)},
        text=True,
        capture_output=True,
        check=False,
    )
    assert invalid.returncode != 0
    assert json.loads(invalid.stdout)["verified"] is False

    ctl = subprocess.run(
        ["bash", str(CTL), "identity"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ctl.returncode == 0, (ctl.stdout, ctl.stderr)
    ctl_payload = json.loads(ctl.stdout.splitlines()[-1])
    assert ctl_payload["identity"]["verified"] is True

print("EVEZ identity runtime tests: PASS")
