#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

MODULE = Path(__file__).with_name("github_verification_ingest.py")
SHA = "a" * 40


def run(bundle: dict) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bundle.json"
        path.write_text(json.dumps(bundle), encoding="utf-8")
        result = subprocess.run([sys.executable, str(MODULE), str(path)], text=True, capture_output=True)
        assert result.returncode == 0, (result.stdout, result.stderr)
        return json.loads(result.stdout)


def bundle(jobs: list[dict], **run_overrides: object) -> dict:
    run = {
        "id": 123,
        "name": "bounded-verification",
        "path": ".github/workflows/bounded.yml",
        "head_sha": SHA,
        "status": "completed",
        "conclusion": "success",
        "html_url": "https://github.com/example/repo/actions/runs/123",
        "event": "pull_request",
        "run_attempt": 1,
    }
    run.update(run_overrides)
    return {"run": run, "jobs": jobs, "candidate_commit": SHA}


def successful_job(job_id: int = 10) -> dict:
    return {
        "id": job_id,
        "name": "epistemic tests",
        "status": "completed",
        "conclusion": "success",
        "started_at": "2026-10-14T12:00:00Z",
        "completed_at": "2026-10-14T12:00:10Z",
        "steps": [
            {"name": "Checkout", "status": "completed", "conclusion": "success", "started_at": "2026-10-14T12:00:00Z"},
            {"name": "Run epistemic tests", "status": "completed", "conclusion": "success", "started_at": "2026-10-14T12:00:02Z"},
        ],
    }


def test_execution_success_is_not_promotion():
    report = run(bundle([successful_job()]))
    assert report["state"] == "EXECUTED_UNVERIFIED"
    assert report["promotion_eligible"] is False
    assert report["jobs"][0]["step_count"] == 2
    assert len(report["source_bundle_sha256"]) == 64


def test_explicit_test_failure_is_failure():
    job = successful_job()
    job["conclusion"] = "failure"
    job["steps"][1]["conclusion"] = "failure"
    report = run(bundle([job], conclusion="failure"))
    assert report["state"] == "FAILED"
    assert report["jobs"][0]["reason_codes"] == ["explicit_test_step_failure"]


def test_setup_failure_is_not_called_code_failure():
    job = successful_job()
    job["conclusion"] = "failure"
    job["steps"][0]["conclusion"] = "failure"
    report = run(bundle([job], conclusion="failure"))
    assert report["state"] == "VERIFIER_INCONCLUSIVE"
    assert "application_result_not_established" in report["jobs"][0]["reason_codes"]


def test_zero_step_no_start_cluster():
    jobs = [
        {"id": n, "name": f"job-{n}", "status": "completed", "conclusion": "failure", "started_at": None, "steps": []}
        for n in range(3)
    ]
    report = run(bundle(jobs, conclusion="failure"))
    assert report["state"] == "VERIFIER_UNAVAILABLE"
    assert report["common_failure_signature"] == "EMPTY_JOB_NO_LOGS_CLUSTER"
    assert report["promotion_eligible"] is False


def test_commit_mismatch_fails_closed():
    report = run(bundle([successful_job()], head_sha="b" * 40))
    assert report["state"] == "VERIFIER_INCONCLUSIVE"
    assert "candidate_run_commit_mismatch" in report["jobs"][0]["reason_codes"]


def test_empty_jobs_are_inconclusive():
    report = run(bundle([]))
    assert report["state"] == "VERIFIER_INCONCLUSIVE"
    assert report["common_failure_signature"] == "NO_JOB_RECORDS"


first = run(bundle([successful_job()]))
second = run(bundle([successful_job()]))
assert first["report_sha256"] == second["report_sha256"]
test_execution_success_is_not_promotion()
test_explicit_test_failure_is_failure()
test_setup_failure_is_not_called_code_failure()
test_zero_step_no_start_cluster()
test_commit_mismatch_fails_closed()
test_empty_jobs_are_inconclusive()
print("GitHub verification evidence ingestion tests: PASS")
