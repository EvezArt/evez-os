#!/usr/bin/env python3
"""Normalize GitHub Actions API run/job/step snapshots into bounded evidence.

This tool never calls GitHub and never promotes a commit. Feed it a saved JSON
bundle from the GitHub Actions API so the exact evidence can be replayed offline.
A successful GitHub job is execution evidence, not independent proof of correctness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
TEST_STEP = re.compile(r"\b(test|tests|pytest|unittest|verification|epistemic|contract|regression|check suite)\b", re.I)
ZERO_STEP_SIGNATURE = "EMPTY_JOB_NO_LOGS_CLUSTER"


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def hash_json(value: Any) -> str:
    return sha256(canonical(value))


def list_value(value: Any) -> list:
    return value if isinstance(value, list) else []


def normalize_job(job: dict[str, Any], run: dict[str, Any], candidate_commit: str | None) -> dict[str, Any]:
    steps = list_value(job.get("steps"))
    run_sha = run.get("head_sha")
    job_sha = job.get("head_sha") or run_sha
    job_conclusion = job.get("conclusion")
    run_conclusion = run.get("conclusion")
    names = [str(step.get("name", "")) for step in steps if isinstance(step, dict)]
    test_steps = [
        step for step in steps
        if isinstance(step, dict) and TEST_STEP.search(str(step.get("name", "")))
    ]
    started_steps = [
        step for step in steps
        if isinstance(step, dict) and step.get("started_at")
    ]
    failed_steps = [
        step for step in steps
        if isinstance(step, dict) and step.get("conclusion") == "failure"
    ]
    failed_test_steps = [
        step for step in test_steps if step.get("conclusion") == "failure"
    ]
    successful_test_steps = [
        step for step in test_steps if step.get("conclusion") == "success"
    ]

    if candidate_commit and run_sha and candidate_commit != run_sha:
        state, reasons = "VERIFIER_INCONCLUSIVE", ["candidate_run_commit_mismatch"]
    elif job_conclusion == "failure" and not steps and not job.get("started_at"):
        state, reasons = "VERIFIER_UNAVAILABLE", ["no_executable_steps", "no_job_start_timestamp"]
    elif job_conclusion == "failure" and not steps:
        state, reasons = "VERIFIER_INCONCLUSIVE", ["job_failed_without_step_evidence"]
    elif failed_test_steps:
        state, reasons = "FAILED", ["explicit_test_step_failure"]
    elif failed_steps:
        state, reasons = "VERIFIER_INCONCLUSIVE", ["non_test_step_failed", "application_result_not_established"]
    elif job_conclusion == "success" and run_conclusion == "success" and successful_test_steps:
        state, reasons = "EXECUTED_UNVERIFIED", ["test_steps_succeeded", "independent_review_not_established"]
    elif not steps or not started_steps:
        state, reasons = "VERIFIER_INCONCLUSIVE", ["execution_boundary_unobserved"]
    else:
        state, reasons = "VERIFIER_INCONCLUSIVE", ["insufficient_test_evidence"]

    return {
        "schema_version": SCHEMA_VERSION,
        "workflow": run.get("name"),
        "workflow_path": run.get("path"),
        "workflow_run_id": run.get("id"),
        "run_attempt": run.get("run_attempt"),
        "run_event": run.get("event"),
        "run_status": run.get("status"),
        "run_conclusion": run_conclusion,
        "candidate_commit": candidate_commit,
        "observed_commit": run_sha,
        "job_id": job.get("id"),
        "job_name": job.get("name"),
        "job_status": job.get("status"),
        "job_conclusion": job_conclusion,
        "job_started_at": job.get("started_at"),
        "job_completed_at": job.get("completed_at"),
        "step_count": len(steps),
        "started_step_count": len(started_steps),
        "test_step_names": [str(step.get("name", "")) for step in test_steps],
        "failed_step_names": [str(step.get("name", "")) for step in failed_steps],
        "state": state,
        "promotion_eligible": False,
        "reason_codes": reasons,
        "run_record_sha256": hash_json(run),
        "job_record_sha256": hash_json(job),
        "step_records_sha256": hash_json(steps),
    }


def normalize_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    run = bundle.get("run")
    jobs = bundle.get("jobs")
    candidate = bundle.get("candidate_commit")
    if not isinstance(run, dict):
        raise ValueError("bundle.run must be an object copied from a GitHub Actions run record")
    if not isinstance(jobs, list) or not all(isinstance(job, dict) for job in jobs):
        raise ValueError("bundle.jobs must be a list of job objects")
    if candidate is not None and (
        not isinstance(candidate, str) or not re.fullmatch(r"[0-9a-f]{40}", candidate)
    ):
        raise ValueError("candidate_commit must be a 40-character lowercase Git SHA")

    normalized = [normalize_job(job, run, candidate) for job in jobs]
    states = [job["state"] for job in normalized]
    if len(normalized) >= 3 and all(state == "VERIFIER_UNAVAILABLE" for state in states):
        state, signature = "VERIFIER_UNAVAILABLE", ZERO_STEP_SIGNATURE
    elif states and all(state == "EXECUTED_UNVERIFIED" for state in states):
        state, signature = "EXECUTED_UNVERIFIED", None
    elif any(state == "FAILED" for state in states):
        state, signature = "FAILED" if all(s == "FAILED" for s in states) else "VERIFIER_INCONCLUSIVE", "MIXED_JOB_RESULTS"
    elif not normalized:
        state, signature = "VERIFIER_INCONCLUSIVE", "NO_JOB_RECORDS"
    elif any(state == "VERIFIER_UNAVAILABLE" for state in states):
        state, signature = "VERIFIER_INCONCLUSIVE", "PARTIAL_RUNNER_UNAVAILABILITY"
    else:
        state, signature = "VERIFIER_INCONCLUSIVE", "INCOMPLETE_EXECUTION_EVIDENCE"

    report = {
        "schema_version": SCHEMA_VERSION,
        "source": "github-actions-api-snapshot",
        "run_id": run.get("id"),
        "run_url": run.get("html_url"),
        "candidate_commit": candidate,
        "observed_commit": run.get("head_sha"),
        "state": state,
        "promotion_eligible": False,
        "common_failure_signature": signature,
        "job_count": len(normalized),
        "jobs": normalized,
        "source_bundle_sha256": hash_json(bundle),
        "rule": "API execution evidence != independent verification != promotion authority",
    }
    report["report_sha256"] = hash_json(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize saved GitHub Actions run/job records.")
    parser.add_argument("bundle", help="JSON object with run, jobs, and optional candidate_commit")
    parser.add_argument("--output", help="optional output path")
    args = parser.parse_args()
    try:
        bundle = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
        if not isinstance(bundle, dict):
            raise ValueError("bundle must be a JSON object")
        report = normalize_bundle(bundle)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"state": "VERIFIER_INCONCLUSIVE", "error": str(exc)}, sort_keys=True))
        return 2
    rendered = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
