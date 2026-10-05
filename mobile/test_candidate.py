#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "mobile" / "evez_candidate.py"


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
        [
            sys.executable,
            str(CANDIDATE),
            "evaluate",
            str(claims_path),
            "--human-approved",
        ],
        text=True,
        capture_output=True,
    )
    assert evaluated.returncode == 0, evaluated.stderr

    result = json.loads(evaluated.stdout)
    assert result["grade"] == "LEAD-QUALIFIED-5"
    assert result["army_status"] == "NONE"
    assert result["authority_status"] == "NONE"

    evaluation_path = Path(temp) / "evaluation.json"
    evaluation_path.write_text(evaluated.stdout, encoding="utf-8")

    packet = subprocess.run(
        [
            sys.executable,
            str(CANDIDATE),
            "packet",
            "candidate-test-001",
            str(evaluation_path),
        ],
        text=True,
        capture_output=True,
    )
    assert packet.returncode == 0, packet.stderr

    packet_data = json.loads(packet.stdout)
    assert packet_data["external_mapping"]["status"] == "not_an_Army_credential"
    assert packet_data["human_action"]["signature"] is None

    claims[0]["result"]["score"] = 1
    tampered = Path(temp) / "tampered.json"
    tampered.write_text(json.dumps(claims), encoding="utf-8")

    degraded = subprocess.run(
        [
            sys.executable,
            str(CANDIDATE),
            "evaluate",
            str(tampered),
            "--human-approved",
        ],
        text=True,
        capture_output=True,
    )
    assert degraded.returncode == 0
    degraded_result = json.loads(degraded.stdout)
    assert degraded_result["grade"] != "LEAD-QUALIFIED-5"

print("defensive candidate qualification test: PASS")
