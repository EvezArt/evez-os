import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = root / "research" / "_precision_spec.json"
spec.write_text(json.dumps({
    "subject": "evez-os",
    "action": "validate intent",
    "scope": "research layer",
    "inputs": ["text"],
    "constraints": ["no consequential actions"],
    "evidence": ["unit test"],
    "acceptance": "exit code 0",
    "time": "one execution cycle",
    "authority": "repository write only",
}), encoding="utf-8")

try:
    ok = subprocess.run(
        [sys.executable, str(root / "mobile" / "evez_precision.py"), "--intent",
         "validate this bounded specification"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert ok.returncode == 0

    bad = subprocess.run(
        [sys.executable, str(root / "mobile" / "evez_precision.py"), "--intent",
         "do everything fully"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert bad.returncode == 2

    valid = subprocess.run(
        [sys.executable, str(root / "mobile" / "evez_precision.py"), "--spec", str(spec)],
        capture_output=True,
        text=True,
        check=True,
    )
    packet = json.loads(valid.stdout)
    assert packet["valid"] is True
finally:
    spec.unlink(missing_ok=True)

print("mobile precision tests: PASS")
