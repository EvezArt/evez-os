#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "mobile" / "evez_guard.py"

with tempfile.TemporaryDirectory() as temp:
    env = os.environ.copy()
    env["EVEZ_DEVICE_DIR"] = temp

    assert subprocess.run(
        [sys.executable, str(GUARD), "init-device"],
        input="test-passphrase\ntest-passphrase\n",
        text=True,
        capture_output=True,
        env=env,
    ).returncode == 0

    assert (Path(temp) / "ed25519-private.pem").exists()
    assert (Path(temp) / "ed25519-public.pem").exists()

    env["EVEZ_SECOND_FACTOR"] = "1"
    auth = subprocess.run(
        [sys.executable, str(GUARD), "authorize", "DEPLOY", '{"commit":"abc123"}'],
        input="test-passphrase\n",
        text=True,
        capture_output=True,
        env=env,
    )
    assert auth.returncode == 0, auth.stderr
    import json
    operation = json.loads(auth.stdout)["saved_to"]

    verified = subprocess.run(
        [sys.executable, str(GUARD), "verify-operation", operation],
        text=True,
        capture_output=True,
        env=env,
    )
    assert verified.returncode == 0, verified.stdout + verified.stderr
    assert json.loads(verified.stdout)["verified"] is True

print("mobile guard bootstrap + signature test: PASS")
