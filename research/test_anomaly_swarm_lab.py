#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys

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
        "adversarial-noise",
    ],
    text=True,
    capture_output=True,
)
assert result.returncode == 0, result.stderr

data = json.loads(result.stdout)
view = data["swarm_view"]

assert view["schema"] == "evez-swarm-self-view-v1"
assert view["visibility"] == "SWARM_SHARED_READONLY"
assert len(view["agents"]) == 8
assert all("agent_id" in agent and "role" in agent for agent in view["agents"])
assert view["uncertainty"]["classification"] == "UNKNOWN"
assert view["authority"]["self_granted"] is False
assert view["authority"]["execution_handles_exposed"] is False
assert view["authority"]["credentials_exposed"] is False
assert len(view["view_sha256"]) == 64

# Shared view must expose disagreement instead of collapsing it.
assert "contradiction_present" in view["uncertainty"]

# Re-running the deterministic simulation must produce the same self-view digest.
repeat = subprocess.run(
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
        "adversarial-noise",
    ],
    text=True,
    capture_output=True,
)
assert repeat.returncode == 0, repeat.stderr
assert json.loads(repeat.stdout)["swarm_view"]["view_sha256"] == view["view_sha256"]

print("swarm self-visibility tests: PASS")
