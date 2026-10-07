import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
output = root / "research" / "_detected_capabilities.json"

try:
    result = subprocess.run(
        [
            sys.executable,
            str(root / "mobile" / "evez_signal_capabilities.py"),
            "--consent-scope",
            "operator-alerts",
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert not result.stdout
    packet = json.loads(output.read_text(encoding="utf-8"))
    assert packet["schema"] == "evez-signal-capabilities-v1"
    assert packet["consent_scopes"] == ["operator-alerts"]
    assert any(row["channel"] == "text" and row["available"] for row in packet["channels"])
    assert all("consent_detected" in row for row in packet["channels"])
finally:
    output.unlink(missing_ok=True)

print("mobile signal capability discovery tests: PASS")
