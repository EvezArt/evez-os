#!/usr/bin/env python3
"""Deterministic classification of verification execution evidence.

This module distinguishes a code failure from a verifier that failed to
produce observable execution evidence. It never promotes, merges, deploys,
or changes authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
STATES = {
    "PROPOSED",
    "EXECUTED_UNVERIFIED",
    "VERIFIED",
    "FAILED",
    "VERIFIER_UNAVAILABLE",
    "VERIFIER_INCONCLUSIVE",
}
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_RE = re.compile(r"^[0-9a-f]{40}$")


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _errors_for_commit(candidate: Any, observed: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(candidate, str) or not GIT_RE.fullmatch(candidate):
        errors.append("candidate_commit_invalid")
    if observed is not None and (
        not isinstance(observed, str) or not GIT_RE.fullmatch(observed)
    ):
        errors.append("observed_commit_invalid")
    if (
        isinstance(candidate, str)
        and isinstance(observed, str)
        and GIT_RE.fullmatch(candidate)
        and GIT_RE.fullmatch(observed)
        and candidate != observed
    ):
        errors.append("source_commit_mismatch")
    return errors


def classify_attempt(evidence: dict[str, Any]) -> dict[str, Any]:
    required = ("candidate_commit", "execution_started", "steps_observed")
    missing = [key for key in required if key not in evidence]
    candidate = evidence.get("candidate_commit")
    observed = evidence.get("observed_commit")
    result = evidence.get("test_result")
    conclusion = evidence.get("conclusion")
    execution_started = evidence.get("execution_started")
    steps_observed = evidence.get("steps_observed")
    steps_expected = evidence.get("steps_expected")
    logs_available = evidence.get("logs_available")
    evidence_complete = evidence.get("evidence_complete", False)
    independent = evidence.get("independent_verifier", False)

    reasons = list(missing)
    reasons.extend(_errors_for_commit(candidate, observed))

    if not isinstance(execution_started, bool):
        reasons.append("execution_started_invalid")
    if not isinstance(steps_observed, int) or steps_observed < 0:
        reasons.append("steps_observed_invalid")
    if steps_expected is not None and (
        not isinstance(steps_expected, int) or steps_expected < 0
    ):
        reasons.append("steps_expected_invalid")
    if logs_available is not None and not isinstance(logs_available, bool):
        reasons.append("logs_available_invalid")
    if not isinstance(evidence_complete, bool):
        reasons.append("evidence_complete_invalid")
    if not isinstance(independent, bool):
        reasons.append("independent_verifier_invalid")
    if result is not None and result not in {"PASS", "FAIL"}:
        reasons.append("test_result_invalid")

    if reasons:
        state = "VERIFIER_INCONCLUSIVE"
    else:
        zero_step_failure = (
            conclusion == "failure"
            and steps_observed == 0
            and logs_available is False
            and execution_started is False
        )

        if zero_step_failure:
            state = "VERIFIER_UNAVAILABLE"
            reasons = ["no_executable_steps", "logs_unavailable"]
        elif conclusion == "failure" and steps_observed == 0:
            state = "VERIFIER_INCONCLUSIVE"
            reasons = ["execution_boundary_unobserved"]
        elif (
            steps_expected is not None
            and steps_observed < steps_expected
        ):
            state = "VERIFIER_INCONCLUSIVE"
            reasons = ["required_steps_not_observed"]
        elif result == "FAIL":
            state = "FAILED"
            reasons = ["executed_test_failed"]
        elif result == "PASS" and not evidence_complete:
            state = "VERIFIER_INCONCLUSIVE"
            reasons = ["execution_evidence_incomplete"]
        elif (
            result == "PASS"
            and evidence_complete
            and independent
            and observed == candidate
        ):
            state = "VERIFIED"
            reasons = ["complete_independent_execution"]
        elif result == "PASS" and evidence_complete:
            state = "EXECUTED_UNVERIFIED"
            reasons = ["execution_observed_without_independent_verifier"]
        else:
            state = "PROPOSED"
            reasons = ["no_execution_result"]

    normalized = {
        "schema_version": SCHEMA_VERSION,
        "candidate_commit": candidate,
        "observed_commit": observed,
        "execution_started": execution_started,
        "steps_observed": steps_observed,
        "steps_expected": steps_expected,
        "logs_available": logs_available,
        "evidence_complete": evidence_complete,
        "independent_verifier": independent,
        "test_result": result,
        "conclusion": conclusion,
        "workflow": evidence.get("workflow"),
        "workflow_run_id": evidence.get("workflow_run_id"),
        "job_id": evidence.get("job_id"),
        "reason_codes": sorted(set(reasons)),
        "state": state,
        "promotion_eligible": state == "VERIFIED",
        "evidence_digest": digest(evidence),
    }
    return normalized


def classify_cluster(jobs: list[dict[str, Any]]) -> dict[str, Any]:
    results = [classify_attempt(job) for job in jobs]
    states = [result["state"] for result in results]
    empty_job_signature = (
        len(results) >= 3
        and all(
            result["state"] == "VERIFIER_UNAVAILABLE"
            and set(result["reason_codes"])
            == {"logs_unavailable", "no_executable_steps"}
            for result in results
        )
    )

    if empty_job_signature:
        cluster_state = "VERIFIER_UNAVAILABLE"
        signature = "EMPTY_JOB_NO_LOGS_CLUSTER"
    elif all(state == "VERIFIED" for state in states):
        cluster_state = "VERIFIED"
        signature = None
    elif any(state == "FAILED" for state in states):
        cluster_state = (
            "FAILED" if all(state == "FAILED" for state in states) else "VERIFIER_INCONCLUSIVE"
        )
        signature = "MIXED_EXECUTION_RESULTS"
    elif any(state == "VERIFIER_UNAVAILABLE" for state in states):
        cluster_state = "VERIFIER_INCONCLUSIVE"
        signature = "PARTIAL_VERIFICATION_AVAILABILITY"
    elif all(state == "EXECUTED_UNVERIFIED" for state in states):
        cluster_state = "EXECUTED_UNVERIFIED"
        signature = None
    else:
        cluster_state = "VERIFIER_INCONCLUSIVE"
        signature = "INCOMPLETE_VERIFICATION_CLUSTER"

    return {
        "schema_version": SCHEMA_VERSION,
        "state": cluster_state,
        "promotion_eligible": cluster_state == "VERIFIED",
        "job_count": len(results),
        "common_failure_signature": signature,
        "jobs": results,
        "evidence_digest": digest(results),
    }


def classify_payload(payload: dict[str, Any]) -> dict[str, Any]:
    jobs = payload.get("jobs")
    if jobs is not None:
        if not isinstance(jobs, list) or not all(isinstance(job, dict) for job in jobs):
            raise ValueError("jobs must be a list of JSON objects")
        return classify_cluster(jobs)
    return classify_attempt(payload)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("evidence must be a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify verification execution evidence without promoting it."
    )
    parser.add_argument("input", help="JSON evidence packet")
    parser.add_argument("output", nargs="?", help="optional output JSON path")
    args = parser.parse_args()

    try:
        report = classify_payload(load(Path(args.input)))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"state": "VERIFIER_INCONCLUSIVE", "error": str(exc)}, sort_keys=True))
        return 1

    rendered = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["state"] in {"VERIFIED", "EXECUTED_UNVERIFIED", "FAILED", "PROPOSED", "VERIFIER_UNAVAILABLE", "VERIFIER_INCONCLUSIVE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
