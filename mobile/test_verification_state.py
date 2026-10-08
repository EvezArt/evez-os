#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULE = ROOT / "verification_state.py"

COMMIT_A = "a" * 40
COMMIT_B = "b" * 40


def classify(payload: dict, expected: str) -> dict:
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / "evidence.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(MODULE), str(path)],
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, (result.stdout, result.stderr)
        report = json.loads(result.stdout)
        assert report["state"] == expected, report
        return report


def base(**overrides: object) -> dict:
    payload = {
        "candidate_commit": COMMIT_A,
        "observed_commit": COMMIT_A,
        "execution_started": True,
        "steps_observed": 5,
        "steps_expected": 5,
        "logs_available": True,
        "evidence_complete": True,
        "independent_verifier": True,
        "test_result": "PASS",
        "conclusion": "success",
        "workflow": "bounded-evolution-receipt",
        "workflow_run_id": 123,
        "job_id": 456,
    }
    payload.update(overrides)
    return payload


# Actual execution failure after steps have run.
failed = classify(
    base(
        test_result="FAIL",
        conclusion="failure",
    ),
    "FAILED",
)
assert failed["promotion_eligible"] is False


# Runner dies before any executable step and exposes no logs.
unavailable = classify(
    base(
        execution_started=False,
        steps_observed=0,
        logs_available=False,
        evidence_complete=False,
        independent_verifier=False,
        test_result=None,
        conclusion="failure",
    ),
    "VERIFIER_UNAVAILABLE",
)
assert set(unavailable["reason_codes"]) == {"logs_unavailable", "no_executable_steps"}


# Partial execution cannot become a code verdict.
inconclusive = classify(
    base(
        steps_observed=2,
        steps_expected=5,
        evidence_complete=False,
        test_result=None,
        conclusion="failure",
    ),
    "VERIFIER_INCONCLUSIVE",
)
assert "required_steps_not_observed" in inconclusive["reason_codes"]


# Successful execution without an independent verifier remains unverified.
reproducible = classify(
    base(
        independent_verifier=False,
    ),
    "EXECUTED_UNVERIFIED",
)
assert reproducible["promotion_eligible"] is False


# Full independent execution with exact source binding is VERIFIED.
verified = classify(base(), "VERIFIED")
assert verified["promotion_eligible"] is True


# A source mismatch is never promoted.
mismatch = classify(
    base(observed_commit=COMMIT_B),
    "VERIFIER_INCONCLUSIVE",
)
assert "source_commit_mismatch" in mismatch["reason_codes"]


# Nine equivalent zero-step jobs produce the cluster signature used for
# infrastructure fault isolation.
jobs = []
for index in range(9):
    jobs.append(
        base(
            execution_started=False,
            steps_observed=0,
            steps_expected=5,
            logs_available=False,
            evidence_complete=False,
            independent_verifier=False,
            test_result=None,
            conclusion="failure",
            workflow=f"workflow-{index}",
            workflow_run_id=100 + index,
            job_id=200 + index,
        )
    )

with tempfile.TemporaryDirectory() as temp:
    path = Path(temp) / "cluster.json"
    path.write_text(json.dumps({"jobs": jobs}), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(MODULE), str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, (result.stdout, result.stderr)
    cluster = json.loads(result.stdout)
    assert cluster["state"] == "VERIFIER_UNAVAILABLE"
    assert cluster["common_failure_signature"] == "EMPTY_JOB_NO_LOGS_CLUSTER"
    assert cluster["job_count"] == 9
    assert cluster["promotion_eligible"] is False

print("verification-state classifier + fault-isolation tests: PASS")
