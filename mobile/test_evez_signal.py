import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
packet = root / "research" / "_test_signal.json"
caps = root / "research" / "_test_capabilities.json"

packet.write_text(json.dumps({
    "signal_id": "sig-test",
    "timestamp": "2026-10-07T18:30:00Z",
    "channel": "text",
    "intent": "CRITICAL",
    "title": "test",
    "payload": {"state": "UNKNOWN"},
    "provenance": {"source": "test"},
    "consent_scope": "operator-alerts",
    "ttl_seconds": 60,
    "priority": 0.95,
}), encoding="utf-8")

caps.write_text(json.dumps({
    "schema": "evez-signal-capabilities-v1",
    "channels": [
        {
            "channel": "audio",
            "available": True,
            "consent_scopes": ["operator-alerts"],
            "attention": 0.9,
            "reliability": 0.85,
            "cost": 1.0,
            "preferred_rank": 1,
        },
        {
            "channel": "haptic",
            "available": True,
            "consent_scopes": ["operator-alerts"],
            "attention": 0.8,
            "reliability": 0.8,
            "cost": 0.5,
            "preferred_rank": 2,
        },
    ],
}), encoding="utf-8")

try:
    result = subprocess.run(
        [
            sys.executable,
            str(root / "mobile" / "evez_signal.py"),
            str(packet),
            "--auto",
            "--capabilities",
            str(caps),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    assert data["dry_run"] is True
    assert data["plan"]["status"] == "READY"
    assert len(data["attempts"]) == 2
    assert data["attempts"][0]["rendered"]["channel"] == "audio"
    assert data["attempts"][1]["rendered"]["channel"] == "haptic"

    manual = subprocess.run(
        [
            sys.executable,
            str(root / "mobile" / "evez_signal.py"),
            str(packet),
            "--channel",
            "audio",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    manual_data = json.loads(manual.stdout)
    assert manual_data["dry_run"] is True
    assert manual_data["attempts"][0]["rendered"]["channel"] == "audio"
    assert len(manual_data["attempts"][0]["rendered"]["digest"]) == 64
finally:
    packet.unlink(missing_ok=True)
    caps.unlink(missing_ok=True)

print("mobile signal adapter tests: PASS")
