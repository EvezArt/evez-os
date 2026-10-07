#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from research.promotion_gate import evaluate
from research.verification_receipt import make_receipt, verify_receipt


receipt = make_receipt(
    candidate_commit="abc123",
    workflow="circleci/verify",
    run_id="364",
    status="success",
    target_url="https://ci.example/run/364",
    required_checks=["mobile-contract", "research-contract"],
    observed_checks=[
        {"name": "mobile-contract", "status": "success"},
        {"name": "research-contract", "status": "success"},
    ],
)
assert verify_receipt(receipt)["valid"]

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

bad_digest = dict(receipt)
bad_digest["digest_sha256"] = "0" * 64
candidate = dict(base)
candidate["ci"] = dict(base["ci"], receipt=bad_digest)
assert evaluate(candidate)["promotable"] is False

wrong_commit = dict(receipt)
wrong_commit["candidate_commit"] = "old"
candidate = dict(base)
candidate["ci"] = dict(base["ci"], receipt=wrong_commit)
assert evaluate(candidate)["promotable"] is False

failed_receipt = make_receipt(
    candidate_commit="abc123",
    workflow="circleci/verify",
    run_id="364",
    status="failure",
    target_url="https://ci.example/run/364",
    required_checks=["mobile-contract"],
    observed_checks=[{"name": "mobile-contract", "status": "failure"}],
)
candidate = dict(base)
candidate["ci"] = dict(base["ci"], receipt=failed_receipt)
assert evaluate(candidate)["promotable"] is False

missing_check = make_receipt(
    candidate_commit="abc123",
    workflow="circleci/verify",
    run_id="364",
    status="success",
    target_url="https://ci.example/run/364",
    required_checks=["mobile-contract", "research-contract"],
    observed_checks=[{"name": "mobile-contract", "status": "success"}],
)
candidate = dict(base)
candidate["ci"] = dict(base["ci"], receipt=missing_check)
assert evaluate(candidate)["promotable"] is False

candidate = dict(base)
candidate["status"] = "REPLICATED"
candidate["independent_replication"] = False
assert evaluate(candidate)["promotable"] is False

print("verification receipt promotion tests: PASS")
