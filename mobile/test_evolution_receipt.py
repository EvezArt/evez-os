#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULE = ROOT / "evolution_receipt.py"


def sha(value):
    return hashlib.sha256(value).hexdigest()


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def make_spec():
    return {
        "source_commit": "a" * 40,
        "working_tree_state": {
            "clean": True,
            "files": [
                {
                    "path": "mobile/evolution_receipt.py",
                    "sha256": sha(MODULE.read_bytes()),
                }
            ],
        },
        "test_manifest": [
            {
                "id": "receipt-self-test",
                "command": [
                    sys.executable,
                    "mobile/test_evolution_receipt.py",
                ],
                "expected_exit_code": 0,
            }
        ],
        "test_results": [
            {
                "id": "receipt-self-test",
                "exit_code": 0,
                "stdout_sha256": sha(b"pass"),
                "stderr_sha256": sha(b""),
                "status": "PASS",
            }
        ],
        "evidence_input_digests": {
            "candidate_source": sha(b"evidence-001")
        },
        "proposal_digest": sha(
            canonical({"task": "evolution-receipt-boundary"})
        ),
        "contradiction_cases": [
            {
                "id": "c-001",
                "claim": "receipt integrity survives tampering",
                "falsifier": "modify one receipt field without recomputing digest",
                "resolution": "must reject with digest mismatch",
                "resolved": True,
            }
        ],
        "failed_attempts": [
            "attempt-0: direct VERIFIED sealing is intentionally blocked"
        ],
        "uncertainties": [
            "receipt verifier does not independently execute external tests"
        ],
        "dissenting_observations": [
            "cryptographic integrity is not equivalent to empirical truth"
        ],
        "verification_status": "PROPOSED",
        "verification_timestamp": "2026-10-07T20:00:00Z",
    }


def run(*args, expect=0):
    result = subprocess.run(
        [sys.executable, str(MODULE), *args],
        text=True,
        capture_output=True,
    )
    assert result.returncode == expect, (
        args,
        result.stdout,
        result.stderr,
    )
    return json.loads(result.stdout)


with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp)
    spec = temp / "spec.json"
    receipt = temp / "receipt.json"
    spec.write_text(json.dumps(make_spec()), encoding="utf-8")

    built = run("build", str(spec), str(receipt))
    assert built["built"] is True

    checked = run("verify", str(receipt))
    assert checked["integrity_verified"] is True
    assert checked["promotion_eligible"] is False
    assert checked["preserved_evidence"]["failed_attempts"] == 1
    assert checked["preserved_evidence"]["uncertainties"] == 1
    assert checked["preserved_evidence"]["dissenting_observations"] == 1

    data = json.loads(receipt.read_text(encoding="utf-8"))
    tampered = copy.deepcopy(data)
    tampered["uncertainties"][0] = "changed after build"
    bad = temp / "tampered.json"
    bad.write_text(json.dumps(tampered), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(MODULE), "verify", str(bad)],
        text=True,
        capture_output=True,
    )
    assert result.returncode != 0
    bad_result = json.loads(result.stdout)
    assert "receipt_digest mismatch" in bad_result["errors"]

    bad_test = copy.deepcopy(data)
    bad_test["test_results"][0]["exit_code"] = 1
    bad_test["test_results"][0]["status"] = "FAIL"
    unsigned = copy.deepcopy(bad_test)
    unsigned.pop("receipt_digest")
    bad_test["receipt_digest"] = hashlib.sha256(
        canonical(unsigned)
    ).hexdigest()
    bad_test_path = temp / "failed-test.json"
    bad_test_path.write_text(json.dumps(bad_test), encoding="utf-8")
    failed = run("verify", str(bad_test_path))
    assert failed["integrity_verified"] is True
    assert failed["promotion_eligible"] is False
    assert failed["test_failures"] == ["receipt-self-test"]

    verified_spec = make_spec()
    verified_spec["verification_status"] = "VERIFIED"
    verified_path = temp / "verified-spec.json"
    verified_path.write_text(
        json.dumps(verified_spec), encoding="utf-8"
    )
    blocked = subprocess.run(
        [
            sys.executable,
            str(MODULE),
            "build",
            str(verified_path),
            str(temp / "blocked.json"),
        ],
        text=True,
        capture_output=True,
    )
    assert blocked.returncode != 0
    assert "refuses to create a VERIFIED receipt" in blocked.stdout

print("evolution receipt integrity + gate tests: PASS")
