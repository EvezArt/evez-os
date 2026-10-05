#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "mobile" / "evez_candidate.py"
AUTHORITY = ROOT / "mobile" / "evez_authority.py"


def digest(competency, evidence_id, measured_at, result):
    return hashlib.sha256(
        json.dumps(
            {
                "competency": competency,
                "evidence_id": evidence_id,
                "measured_at": measured_at,
                "result": result,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()


with tempfile.TemporaryDirectory() as temp:
    env = os.environ.copy()
    env["EVEZ_AUTHORITY_DIR"] = temp

    init = subprocess.run(
        [sys.executable, str(AUTHORITY), "init-role", "reviewer"],
        text=True,
        input="test-pass\ntest-pass\n",
        capture_output=True,
        env=env,
    )
    assert init.returncode == 0, init.stderr

    claims = []
    timestamp = "2026-10-05T00:00:00Z"

    for index, competency in enumerate(
        [
            "evidence_integrity",
            "secure_channels",
            "incident_response",
            "recovery",
            "supply_chain",
            "human_command",
        ]
    ):
        result = {"score": 95}
        claims.append(
            {
                "competency": competency,
                "evidence_id": f"e-{index}",
                "measured_at": timestamp,
                "result": result,
                "source_sha256": digest(
                    competency, f"e-{index}", timestamp, result
                ),
            }
        )

    claims_path = Path(temp) / "claims.json"
    claims_path.write_text(json.dumps(claims), encoding="utf-8")

    evaluated = subprocess.run(
        [sys.executable, str(CANDIDATE), "evaluate", str(claims_path)],
        text=True,
        capture_output=True,
        env=env,
    )
    assert evaluated.returncode == 0, evaluated.stderr
    evaluation = json.loads(evaluated.stdout)
    assert evaluation["provisional_grade"] == "CANDIDATE-0"
    assert evaluation["recommended_grade_after_human_review"] == "LEAD-QUALIFIED-5"
    assert evaluation["human_approval_present"] is False

    evaluation_path = Path(temp) / "evaluation.json"
    evaluation_path.write_text(evaluated.stdout, encoding="utf-8")

    material = {k: v for k, v in evaluation.items() if k not in {"human_review"}}
    evaluation_sha = hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    payload = json.dumps(
        {
            "candidate_id": "candidate-test-001",
            "evaluation_sha256": evaluation_sha,
        },
        separators=(",", ":"),
    )

    signed = subprocess.run(
        [
            sys.executable,
            str(AUTHORITY),
            "sign",
            "reviewer",
            "PROMOTE_CANDIDATE",
            payload,
            "--operation-id",
            "promotion-001",
        ],
        text=True,
        input="test-pass\n",
        capture_output=True,
        env=env,
    )
    assert signed.returncode == 0, signed.stderr
    operation = json.loads(signed.stdout)["saved_to"]

    promoted = subprocess.run(
        [
            sys.executable,
            str(CANDIDATE),
            "promote",
            "candidate-test-001",
            str(evaluation_path),
            operation,
            str(Path(temp) / "reviewer-public.pem"),
        ],
        text=True,
        capture_output=True,
        env=env,
    )
    assert promoted.returncode == 0, promoted.stderr
    packet = json.loads(promoted.stdout)
    assert packet["qualification"]["grade"] == "LEAD-QUALIFIED-5"
    assert packet["human_action"]["approved"] is True
    assert packet["external_mapping"]["status"] == "not_an_Army_credential"

    claims[0]["result"]["score"] = 1
    tampered = Path(temp) / "tampered.json"
    tampered.write_text(json.dumps(claims), encoding="utf-8")

    degraded = subprocess.run(
        [sys.executable, str(CANDIDATE), "evaluate", str(tampered)],
        text=True,
        capture_output=True,
        env=env,
    )
    assert degraded.returncode == 0
    degraded_result = json.loads(degraded.stdout)
    assert degraded_result["recommended_grade_after_human_review"] != "LEAD-QUALIFIED-5"

print("defensive candidate signed-promotion test: PASS")
