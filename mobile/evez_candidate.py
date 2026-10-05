#!/usr/bin/env python3
"""EVEZ Defensive Cyber Candidate / qualification ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "training" / "candidate-policy.json"


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class Grade:
    name: str
    minimum_total: int
    required: tuple[str, ...]
    human_approval: bool


GRADES = (
    Grade("CANDIDATE-0", 0, ("evidence_integrity",), False),
    Grade("QUALIFIED-1", 500, ("evidence_integrity", "secure_channels"), True),
    Grade("QUALIFIED-2", 700, ("evidence_integrity", "secure_channels", "incident_response"), True),
    Grade("QUALIFIED-3", 820, ("evidence_integrity", "secure_channels", "incident_response", "recovery"), True),
    Grade("SENIOR-QUALIFIED-4", 900, ("evidence_integrity", "secure_channels", "incident_response", "recovery", "supply_chain"), True),
    Grade("LEAD-QUALIFIED-5", 950, ("evidence_integrity", "secure_channels", "incident_response", "recovery", "supply_chain", "human_command"), True),
)


def load_policy() -> dict:
    with POLICY.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise SystemExit("candidate policy must be a JSON object")
    return value


def validate_claim(name: str, data: dict, claim: dict) -> tuple[bool, int, str]:
    required = {
        "competency",
        "evidence_id",
        "measured_at",
        "result",
        "source_sha256",
    }
    if not required.issubset(claim):
        return False, 0, "missing claim fields"

    if claim["competency"] != name:
        return False, 0, "competency mismatch"

    expected = hashlib.sha256(
        canonical(
            {
                "competency": claim["competency"],
                "evidence_id": claim["evidence_id"],
                "measured_at": claim["measured_at"],
                "result": claim["result"],
            }
        )
    ).hexdigest()

    if expected != claim["source_sha256"]:
        return False, 0, "evidence digest mismatch"

    score_cap = int(data.get("max_points", 100))
    score = int(claim["result"].get("score", 0))
    if score < 0 or score > score_cap:
        return False, 0, "score outside policy bounds"

    return True, score * int(data.get("weight", 1)), "valid"


def evaluate(claims: list[dict], human_approved: bool) -> dict:
    policy = load_policy()
    competencies = policy["competencies"]
    scores: dict[str, int] = {}
    evidence: list[dict] = []
    failures: list[str] = []

    for name, data in competencies.items():
        matching = [c for c in claims if c.get("competency") == name]
        if not matching:
            scores[name] = 0
            continue

        best = 0
        best_record = None
        for claim in matching:
            valid, value, reason = validate_claim(name, data, claim)
            evidence.append(
                {
                    "competency": name,
                    "evidence_id": claim.get("evidence_id"),
                    "valid": valid,
                    "reason": reason,
                    "points": value,
                }
            )
            if valid and value > best:
                best = value
                best_record = claim

        scores[name] = best
        if best_record is None:
            failures.append(name)

    total = sum(scores.values())
    earned = GRADES[0]

    for grade in GRADES:
        required_ok = all(scores.get(name, 0) > 0 for name in grade.required)
        approval_ok = human_approved or not grade.human_approval
        if total >= grade.minimum_total and required_ok and approval_ok:
            earned = grade

    return {
        "evaluated_at": now(),
        "grade": earned.name,
        "total_points": total,
        "competency_scores": scores,
        "required_evidence": list(earned.required),
        "human_approval_required": earned.human_approval,
        "human_approval_present": human_approved,
        "invalid_or_missing_competencies": failures,
        "evidence_review": evidence,
        "army_status": "NONE",
        "authority_status": "NONE",
        "note": "EVEZ internal qualification only; not military rank, enlistment, clearance, or command authority.",
    }


def promotion_packet(candidate_id: str, evaluation: dict) -> dict:
    packet = {
        "packet_version": 1,
        "candidate_id": candidate_id,
        "created_at": now(),
        "qualification": evaluation,
        "external_mapping": {
            "reference": "U.S. Army 17C Cyber Operations Specialist",
            "purpose": "public competency reference only",
            "status": "not_an_Army_credential",
        },
        "human_action": {
            "required": evaluation["human_approval_required"],
            "approved": evaluation["human_approval_present"],
            "signature": None,
        },
    }
    packet["packet_sha256"] = hashlib.sha256(canonical(packet)).hexdigest()
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("claims_file")
    p_eval.add_argument("--human-approved", action="store_true")

    p_packet = sub.add_parser("packet")
    p_packet.add_argument("candidate_id")
    p_packet.add_argument("evaluation_file")

    args = parser.parse_args()

    if args.command == "evaluate":
        claims = json.loads(Path(args.claims_file).read_text(encoding="utf-8"))
        if not isinstance(claims, list):
            raise SystemExit("claims file must be a JSON array")
        print(json.dumps(evaluate(claims, args.human_approved), indent=2, sort_keys=True))
        return 0

    if args.command == "packet":
        evaluation = json.loads(Path(args.evaluation_file).read_text(encoding="utf-8"))
        print(json.dumps(promotion_packet(args.candidate_id, evaluation), indent=2, sort_keys=True))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
