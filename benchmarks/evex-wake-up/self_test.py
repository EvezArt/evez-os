#!/usr/bin/env python3
"""Self-test the EVEX Wake-Up benchmark, including rejection of unsafe promotion."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERIFY = ROOT / "verify.py"
REFERENCE = ROOT / "expected-receipt.evex.json"
NEGATIVE = ROOT / "negative-promotion.evex.json"


def run(path: Path) -> int:
    return subprocess.run(
        [sys.executable, str(VERIFY), str(path)],
        cwd=ROOT.parent.parent.parent,
        check=False,
    ).returncode


good = run(REFERENCE)
bad = run(NEGATIVE)

if good != 0:
    raise SystemExit("FAIL self-test: reference receipt was rejected")

if bad == 0:
    raise SystemExit("FAIL self-test: unsafe epistemic promotion was accepted")

print("PASS EVEX Wake-Up self-test")
print("reference=accepted")
print("negative-promotion=rejected")
