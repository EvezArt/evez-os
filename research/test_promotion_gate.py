#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from research.promotion_gate import evaluate
from research.verification_receipt import make_receipt

receipt = make_receipt(
    candidate_commit="abc123",
    workflow="circleci/verify",
    run_id="364",
    status="success",
    target_url="https://ci.example/run/364",
    required_checks=["mobile-contract"],
    observed_checks=[{"name": "mobile-contract", "status": "success"}],
)

base = {
    "status": "MEASURED",
    "provenance": {"commit_sha": "abc123"},
    "ci": {
        "verified": True,
        "status": "success",
        "commit_sha": "abc123",
        "receipt": receipt,
    },
    "uncertainty": ["sampling error"],
    "dissent": ["common-cause confound remains possible"],
    "measurement_source": "sensor-01",
}

assert evaluate(base)["promotable"] is True

for field, value in [
    ("ci", {"verified": True, "status": "success", "commit_sha": "old", "receipt": receipt}),
    ("ci", {"verified": True, "status": "failure", "commit_sha": "abc123", "receipt": receipt}),
    ("ci", {"verified": False, "status": "success", "commit_sha": "abc123", "receipt": receipt}),
]:
    candidate = dict(base)
    candidate[field] = value
    result = evaluate(candidate)
    assert result["promotable"] is False, result

bad_receipt = dict(receipt)
bad_receipt["candidate_commit"] = "old"
candidate = dict(base)
candidate["ci"] = dict(base["ci"], receipt=bad_receipt)
assert evaluate(candidate)["promotable"] is False

candidate = dict(base)
candidate["status"] = "REPLICATED"
candidate["independent_replication"] = False
assert evaluate(candidate)["promotable"] is False

print("promotion gate adversarial tests: PASS")
