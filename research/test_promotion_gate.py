#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from research.promotion_gate import evaluate

base = {
    "status": "MEASURED",
    "provenance": {"commit_sha": "abc123"},
    "ci": {"verified": True, "status": "success", "commit_sha": "abc123"},
    "uncertainty": ["sampling error"],
    "dissent": ["common-cause confound remains possible"],
    "measurement_source": "sensor-01",
}

assert evaluate(base)["promotable"] is True

for field, value in [
    ("ci", {"verified": True, "status": "success", "commit_sha": "old"}),
    ("ci", {"verified": True, "status": "failure", "commit_sha": "abc123"}),
    ("ci", {"verified": False, "status": "success", "commit_sha": "abc123"}),
]:
    candidate = dict(base)
    candidate[field] = value
    result = evaluate(candidate)
    assert result["promotable"] is False, result

candidate = dict(base)
candidate["status"] = "REPLICATED"
candidate["independent_replication"] = False
assert evaluate(candidate)["promotable"] is False

print("promotion gate adversarial tests: PASS")
