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

print("mobile guard bootstrap test: PASS")
