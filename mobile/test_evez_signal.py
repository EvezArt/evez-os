import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
packet = root / "research" / "_test_signal.json"
packet.write_text(json.dumps({
    "signal_id": "sig-test",
    "timestamp": "2026-10-07T18:30:00Z",
    "channel": "text",
    "intent": "INFO",
    "title": "test",
    "payload": {"state": "UNKNOWN"},
    "provenance": {"source": "test"},
    "consent_scope": "test",
    "ttl_seconds": 60,
    "priority": 0.5,
}), encoding="utf-8")

try:
    result = subprocess.run(
        [sys.executable, str(root / "mobile" / "evez_signal.py"),
         str(packet), "--channel", "audio"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    assert data["dry_run"] is True
    assert data["rendered"]["channel"] == "audio"
    assert len(data["rendered"]["digest"]) == 64
finally:
    packet.unlink(missing_ok=True)

print("mobile signal adapter tests: PASS")
