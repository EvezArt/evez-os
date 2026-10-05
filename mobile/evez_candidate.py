#!/usr/bin/env python3
"""EVEZ Defensive Cyber Candidate qualification and promotion runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import evez_authority

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "training" / "candidate-policy.json"


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def evaluation_sha256(evaluation: dict) -> str:
    material = {k: v for k, v in evaluation.items() if k not in {"human_review"}}
    return hashlib.sha256(canonical(material)).hexdigest()


class Grade:
    def __init__(self, name: str, minimum_total: int, required: tuple[str, ...], human_approval: bool):
        self.name = name
        self.minimum_total = minimum_total
        self.required = required
        self.human_approval = human_approval


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


def grade_for(scores: dict[str, int], total: int, human_approved: bool) -> Grade:
    earned = GRADES[0]
    for grade in GRADES:
        required_ok = all(scores.get(name, 0) > 0 for name in grade.required)
        approval_ok = human_approved or not grade.human_approval
        if total >= grade.minimum_total and required_ok and approval_ok:
            earned = grade
    return earned


def validate_claim(name: str, data: dict, claim: dict) -> tuple[bool, int, str]:
    required = {"competency", "evidence_id", "measured_at", "result", "source_sha256"}
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


def evaluate(claims: list[dict]) -> dict:
    policy = load_policy()
    competencies = policy["competencies"]
    scores: dict[str, int] = {}
    evidence: list[dict] = []
    failures: list[str] = []

    for name, data in competencies.items():
        matching = [claim for claim in claims if claim.get("competency") == name]
        if not matching:
            scores[name] = 0
            failures.append(name)
            continue

        best = 0
        valid_any = False
        for claim in matching:
            valid, points, reason = validate_claim(name, data, claim)
            evidence.append(
                {
                    "competency": name,
                    "evidence_id": claim.get("evidence_id"),
                    "valid": valid,
                    "reason": reason,
                    "points": points,
                }
            )
            if valid:
                valid_any = True
                best = max(best, points)

        scores[name] = best
        if not valid_any:
            failures.append(name)

    total = sum(scores.values())
    recommended = grade_for(scores, total, True)
    provisional = grade_for(scores, total, False)

    return {
        "evaluated_at": now(),
        "recommended_grade_after_human_review": recommended.name,
        "provisional_grade": provisional.name,
        "total_points": total,
        "competency_scores": scores,
        "required_evidence_for_recommended_grade": list(recommended.required),
        "human_approval_required": recommended.human_approval,
        "human_approval_present": False,
        "invalid_or_missing_competencies": failures,
        "evidence_review": evidence,
        "army_status": "NONE",
        "authority_status": "NONE",
        "note": "EVEZ internal qualification only; not military rank, enlistment, clearance, or command authority.",
    }


def promote(candidate_id: str, evaluation: dict, reviewer_operation: str, reviewer_public: str) -> dict:
    expected_eval_sha = evaluation_sha256(evaluation)
    approval = evez_authority.verify(reviewer_operation, reviewer_public, "reviewer")

    if not approval.get("verified"):
        raise SystemExit("DENY: reviewer authority envelope did not verify")

    operation = json.loads(Path(reviewer_operation).read_text(encoding="utf-8"))
    envelope = operation["envelope"]

    if envelope["action"] != "PROMOTE_CANDIDATE":
        raise SystemExit("DENY: reviewer envelope action is not PROMOTE_CANDIDATE")

    payload = envelope["payload"]
    if payload.get("candidate_id") != candidate_id:
        raise SystemExit("DENY: candidate identity mismatch")

    if payload.get("evaluation_sha256") != expected_eval_sha:
        raise SystemExit("DENY: evaluation digest mismatch")

    final_grade = evaluation["recommended_grade_after_human_review"]
    final = dict(evaluation)
    final["provisional_grade"] = final_grade
    final["grade"] = final_grade
    final["human_approval_present"] = True
    final["human_review"] = {
        "role": "reviewer",
        "operation_id": envelope["operation_id"],
        "epoch": envelope["epoch"],
        "message_sha256": operation["message_sha256"],
        "public_key_sha256": operation["public_key_sha256"],
    }

    packet = {
        "packet_version": 2,
        "candidate_id": candidate_id,
        "created_at": now(),
        "qualification": final,
        "external_mapping": {
            "reference": "U.S. Army 17C Cyber Operations Specialist",
            "purpose": "public competency reference only",
            "status": "not_an_Army_credential",
        },
        "human_action": {
            "required": True,
            "approved": True,
            "approval_operation_id": envelope["operation_id"],
        },
    }
    packet["packet_sha256"] = hashlib.sha256(canonical(packet)).hexdigest()
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("claims_file")

    p_promote = sub.add_parser("promote")
    p_promote.add_argument("candidate_id")
    p_promote.add_argument("evaluation_file")
    p_promote.add_argument("reviewer_operation")
    p_promote.add_argument("reviewer_public")

    args = parser.parse_args()

    if args.command == "evaluate":
        claims = json.loads(Path(args.claims_file).read_text(encoding="utf-8"))
        if not isinstance(claims, list):
            raise SystemExit("claims file must be a JSON array")
        print(json.dumps(evaluate(claims), indent=2, sort_keys=True))
        return 0

    if args.command == "promote":
        evaluation = json.loads(Path(args.evaluation_file).read_text(encoding="utf-8"))
        packet = promote(
            args.candidate_id,
            evaluation,
            args.reviewer_operation,
            args.reviewer_public,
        )
        print(json.dumps(packet, indent=2, sort_keys=True))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
