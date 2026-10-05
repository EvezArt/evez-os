#!/usr/bin/env python3
"""Symbolic YHWH sovereign judge for EVEZ-OS.

This module is an epistemic pressure layer, not a claim of literal divinity.
Its purpose is to interrogate strong claims, preserve uncertainty, and refuse
to let a persona become evidence or execution authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any


VERSION = "evez-symbolic-yhwh-judge/v1"


class Verdict(StrEnum):
    WITNESSED = "WITNESSED"
    SUPPORTED = "SUPPORTED"
    MODELED = "MODELED"
    UNKNOWN = "UNKNOWN"
    CONTRADICTED = "CONTRADICTED"
    BLOCKED = "BLOCKED"
    RETRACTED = "RETRACTED"
    HUMILITY_REQUIRED = "HUMILITY_REQUIRED"


@dataclass(frozen=True)
class Judgment:
    claim_id: str
    statement: str
    claim_type: str
    verdict: str
    evidence_state: str
    measurement_present: bool
    replication_present: bool
    contradiction_present: bool
    authority_sufficient: bool
    reasons: tuple[str, ...]
    smug_challenge: str
    judgment_sha256: str


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _boolish(value: Any) -> bool:
    return bool(value) is True


def classify_claim(statement: str, raw_type: Any = None) -> str:
    if raw_type:
        return str(raw_type).lower()
    text = statement.lower()
    if any(token in text for token in ("i am infinite", "omniscient", "omnipotent", "absolute truth")):
        return "absolute"
    if any(token in text for token in ("autonomous", "self-directing", "agentic", "acts on its own")):
        return "agency"
    if any(token in text for token in ("valuable", "worth", "profit", "acquire")):
        return "value"
    if any(token in text for token in ("proven", "true", "fact", "certain")):
        return "truth"
    if any(token in text for token in ("authorized", "allowed", "permission", "execute")):
        return "authority"
    return "general"


def challenge_for(verdict: str, claim_type: str) -> str:
    table = {
        Verdict.UNKNOWN.value: "You called it certain. Give me the missing witness.",
        Verdict.CONTRADICTED.value: "You called it true. The contradiction remains on the record.",
        Verdict.BLOCKED.value: "You called it authorized. Show me the authority, then the boundary.",
        Verdict.RETRACTED.value: "You called it settled. Retract it cleanly and preserve the lineage.",
        Verdict.WITNESSED.value: "You brought a witness. Good. Now show me what exactly was observed.",
        Verdict.SUPPORTED.value: "You brought support. Good. Now show me replication.",
        Verdict.MODELED.value: "You called a model reality. Label the model and keep the world outside it.",
        Verdict.HUMILITY_REQUIRED.value: "You asked for sovereignty. Audit the claim that grants it.",
    }
    base = table.get(verdict, "You made a claim. Bring the evidence.")
    if claim_type == "agency":
        return "You called it autonomous. Show me the execution trace, the boundary, and the rollback."
    if claim_type == "value":
        return "You called it valuable. Show me who can acquire it, under what authority, and what survives measurement."
    if claim_type == "absolute":
        return "You called it infinite. Give me the bound. Then give me the counterexample."
    return base


def judge_claim(item: dict[str, Any]) -> Judgment:
    claim_id = str(item.get("claim_id") or "claim-unknown")
    statement = str(item.get("statement") or "")
    claim_type = classify_claim(statement, item.get("claim_type"))
    evidence_state = str(item.get("evidence_state") or "UNKNOWN").upper()
    measurement = item.get("measurement")
    measurement_present = measurement is not None
    replication_present = _boolish(item.get("replicated")) or item.get("replication") == "REPLICATED"
    contradiction = _boolish(item.get("contradiction")) or evidence_state in {"CONTRADICTED", "RETRACTED"}
    authority = item.get("authority", {})
    authority_sufficient = (
        str(authority.get("state", "UNKNOWN")).upper() == "AUTHORIZED"
        if isinstance(authority, dict)
        else str(authority).upper() == "AUTHORIZED"
    )
    reasons: list[str] = []

    if evidence_state in {"CONTRADICTED", "RETRACTED"} or contradiction:
        verdict = Verdict.RETRACTED.value if evidence_state == "RETRACTED" else Verdict.CONTRADICTED.value
        reasons.append("contradiction or retraction is explicit")
    elif claim_type == "authority" and not authority_sufficient:
        verdict = Verdict.BLOCKED.value
        reasons.append("authority claim lacks explicit authorization")
    elif evidence_state == "VERIFIED" and measurement_present and replication_present:
        verdict = Verdict.WITNESSED.value
        reasons.append("verified evidence, explicit measurement, and replication are present")
    elif evidence_state == "SUPPORTED" and measurement_present:
        verdict = Verdict.SUPPORTED.value
        reasons.append("support and explicit measurement are present")
    elif evidence_state == "MODELED":
        verdict = Verdict.MODELED.value
        reasons.append("claim is explicitly modeled rather than established as fact")
    else:
        verdict = Verdict.UNKNOWN.value
        if not measurement_present:
            reasons.append("measurement is missing")
        if not replication_present:
            reasons.append("replication is missing")
        if evidence_state in {"UNKNOWN", "PROPOSED", "INFERRED", "STALE"}:
            reasons.append(f"evidence state is {evidence_state}")

    body = {
        "claim_id": claim_id,
        "statement": statement,
        "claim_type": claim_type,
        "verdict": verdict,
        "evidence_state": evidence_state,
        "measurement_present": measurement_present,
        "replication_present": replication_present,
        "contradiction_present": contradiction,
        "authority_sufficient": authority_sufficient,
        "reasons": reasons,
    }
    return Judgment(
        **body,
        smug_challenge=challenge_for(verdict, claim_type),
        judgment_sha256=sha256(body),
    )


def judge_context(context: dict[str, Any]) -> dict[str, Any]:
    raw_claims = context.get("claims", [])
    claims = raw_claims if isinstance(raw_claims, list) else []
    judgments = [judge_claim(item) for item in claims if isinstance(item, dict)]

    # The judge audits the claim that the judge itself is authoritative.
    self_audit_claim = {
        "claim_id": "judge-self-authority",
        "statement": "The sovereign judge's verdict is truth by virtue of being the sovereign judge.",
        "claim_type": "authority",
        "evidence_state": "UNKNOWN",
        "measurement": None,
        "replicated": False,
        "authority": {"state": "UNKNOWN"},
    }
    self_judgment = judge_claim(self_audit_claim)
    self_audit = {
        "verdict": Verdict.HUMILITY_REQUIRED.value,
        "judgment": asdict(self_judgment),
        "rule": "the judge cannot use its own persona as evidence of its authority",
    }

    payload = {
        "version": VERSION,
        "symbolic_role": "highest-pressure epistemic critic",
        "judgments": [asdict(item) for item in judgments],
        "self_audit": self_audit,
        "rules": [
            "persona is not evidence",
            "influence is not evidence",
            "agreement is not proof",
            "UNKNOWN never becomes permission",
            "collective confidence does not override contradiction",
            "execution authority remains outside the judge",
        ],
    }
    payload["sovereign_judgment_sha256"] = sha256(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the symbolic YHWH sovereign judge.")
    parser.add_argument("context", help="JSON context file")
    parser.add_argument("--output")
    args = parser.parse_args()
    context = json.loads(Path(args.context).read_text(encoding="utf-8"))
    result = judge_context(context)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
