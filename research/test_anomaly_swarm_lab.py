#!/usr/bin/env python3
import json
import subprocess
import sys

for mode in ("clean", "noisy", "partitioned", "adversarial-noise"):
    result = subprocess.run(
        [
            sys.executable,
            "research/anomaly_swarm_lab.py",
            "--seed",
            "777",
            "--agents",
            "8",
            "--ticks",
            "12",
            "--degradation",
            mode,
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr

    data = json.loads(result.stdout)

    assert data["unknown_classification"] == "UNKNOWN"
    assert data["authority"]["self_granted"] is False
    assert data["authority"]["autonomous_physical_action"] is False
    assert 0 <= data["metrics"]["emergence"] <= 1
    assert len(data["result_sha256"]) == 64

print("anomaly swarm lab test: PASS")
