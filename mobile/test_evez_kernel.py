import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
budget = root / "research" / "_kernel_budget.json"
requests = root / "research" / "_kernel_requests.json"
channels = root / "research" / "_kernel_channels.json"

budget.write_text(json.dumps({
    "compute": 10,
    "memory_mb": 2048,
    "latency_ms": 5000,
    "energy": 10,
    "network_mb": 100,
    "attention": 5,
    "monetary": 1,
}), encoding="utf-8")

requests.write_text(json.dumps([{
    "operation_id": "build",
    "expected_value": 3,
    "expected_information_gain": 2,
    "urgency": 1,
    "risk": 0.1,
    "resources": {
        "compute": 2,
        "memory_mb": 256,
        "latency_ms": 500,
        "energy": 1,
        "network_mb": 2,
        "attention": 1,
        "monetary": 0.1,
    },
}]), encoding="utf-8")

channels.write_text(json.dumps({
    "channels": [{
        "channel": "visual",
        "available": True,
        "consent_scopes": ["operator-info"],
        "attention": 0.9,
        "reliability": 0.9,
        "cost": 1,
        "preferred_rank": 1,
    }]
}), encoding="utf-8")

try:
    result = subprocess.run([
        sys.executable,
        str(root / "mobile" / "evez_kernel.py"),
        "build the missing capability",
        "--budget", str(budget),
        "--requests", str(requests),
        "--channels", str(channels),
    ], capture_output=True, text=True, check=True)
    packet = json.loads(result.stdout)
    assert packet["status"] == "READY_FOR_VERIFICATION"
    assert packet["authorization"]["consequential_execution_blocked"] is False
    assert packet["signal"]["signal_digest"]
finally:
    for path in (budget, requests, channels):
        path.unlink(missing_ok=True)

print("mobile execution kernel tests: PASS")
