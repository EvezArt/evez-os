#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULE = ROOT / "evolution_receipt.py"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def run(*args: str, expect: int = 0) -> dict:
    result = subprocess.run(
        [sys.executable, str(MODULE), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == expect, (args, result.stdout, result.stderr)
    return json.loads(result.stdout)


def git(cwd: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(cwd), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, (args, result.stdout, result.stderr)


with tempfile.TemporaryDirectory() as temp:
    temp_path = Path(temp)
    repo = temp_path / "repo"
    repo.mkdir()

    git(repo, "init")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "receipt-test")

    tracked = repo / "tracked.txt"
    tracked.write_text("alpha\n", encoding="utf-8")
    git(repo, "add", "tracked.txt")
    git(repo, "commit", "-m", "fixture")
    source_commit = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()

    proposal = {
        "schema_version": 1,
        "source_commit": "0" * 40,
        "working_tree_state": {
            "clean": True,
            "files": [{"path": "tracked.txt", "sha256": "0" * 64}],
        },
        "test_manifest": [
            {
                "id": "fixture",
                "command": [sys.executable, "-c", "print('pass')"],
                "expected_exit_code": 0,
            }
        ],
        "test_results": [
            {
                "id": "fixture",
                "exit_code": 0,
                "stdout_sha256": sha(b"pass\n"),
                "stderr_sha256": sha(b""),
                "status": "PASS",
            }
        ],
        "evidence_input_digests": {"fixture": sha(b"evidence")},
        "proposal_digest": sha(canonical({"task": "capture"})),
        "contradiction_cases": [
            {
                "id": "c-001",
                "claim": "provenance binds to checkout",
                "falsifier": "alter tracked file after capture",
                "resolution": "verify-against must fail",
                "resolved": True,
            }
        ],
        "failed_attempts": ["first implementation accepted self-declared provenance"],
        "uncertainties": ["test_results remain observational claims until an external runner executes them"],
        "dissenting_observations": ["hash integrity is not truth"],
        "verification_status": "PROPOSED",
        "verification_timestamp": "2026-10-07T00:00:00Z",
        "receipt_digest": "0" * 64,
    }

    input_path = temp_path / "proposal.json"
    captured_path = temp_path / "captured.json"
    receipt_path = temp_path / "receipt.json"
    input_path.write_text(json.dumps(proposal), encoding="utf-8")

    captured = subprocess.run(
        [sys.executable, str(MODULE), "capture", str(repo), str(input_path), str(captured_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert captured.returncode == 0, (captured.stdout, captured.stderr)
    captured_spec = json.loads(captured_path.read_text(encoding="utf-8"))
    assert captured_spec["source_commit"] == source_commit
    assert captured_spec["working_tree_state"]["clean"] is True
    assert len(captured_spec["working_tree_state"]["files"]) == 1

    built = run("build", str(captured_path), str(receipt_path))
    assert built["built"] is True

    checked = run("verify", str(receipt_path))
    assert checked["integrity_verified"] is True
    assert checked["promotion_eligible"] is False
    assert checked["preserved_evidence"]["failed_attempts"] == 1
    assert checked["preserved_evidence"]["uncertainties"] == 1
    assert checked["preserved_evidence"]["dissenting_observations"] == 1

    against = run("verify-against", str(receipt_path), str(repo))
    assert against["integrity_verified"] is True
    assert against["environment_match"] is True

    tracked.write_text("tampered\n", encoding="utf-8")
    bad_env = subprocess.run(
        [sys.executable, str(MODULE), "verify-against", str(receipt_path), str(repo)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert bad_env.returncode != 0
    bad_details = json.loads(bad_env.stdout)
    assert bad_details["environment_match"] is False
    assert any("file digest mismatch" in item for item in bad_details["errors"])

    tampered = copy.deepcopy(json.loads(receipt_path.read_text(encoding="utf-8")))
    tampered["uncertainties"][0] = "changed"
    tampered_path = temp_path / "tampered.json"
    tampered_path.write_text(json.dumps(tampered), encoding="utf-8")
    bad_receipt = subprocess.run(
        [sys.executable, str(MODULE), "verify", str(tampered_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert bad_receipt.returncode != 0
    assert "receipt_digest mismatch" in json.loads(bad_receipt.stdout)["errors"]

    verified_spec = copy.deepcopy(captured_spec)
    verified_spec["verification_status"] = "VERIFIED"
    verified_path = temp_path / "verified-spec.json"
    verified_path.write_text(json.dumps(verified_spec), encoding="utf-8")
    blocked = subprocess.run(
        [sys.executable, str(MODULE), "build", str(verified_path), str(temp_path / "blocked.json")],
        text=True,
        capture_output=True,
        check=False,
    )
    assert blocked.returncode != 0
    assert "refuses to create a VERIFIED receipt" in blocked.stdout

print("evolution receipt provenance + failure-gate tests: PASS")
