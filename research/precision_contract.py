#!/usr/bin/env python3
"""Reject vague outcome language before it becomes executable state."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from typing import Any

VAGUE_TERMS = (
    "do it",
    "everything",
    "all",
    "soon",
    "later",
    "better",
    "best",
    "good",
    "great",
    "optimal",
    "fully",
    "complete",
    "perfect",
    "unprecedented",
    "extraordinary",
    "significant",
    "appropriate",
    "reasonable",
    "safe",
    "secure",
    "real",
    "works",
    "working",
    "fix it",
    "make it happen",
    "as needed",
    "etc",
)

REQUIRED_FIELDS = (
    "subject",
    "action",
    "scope",
    "inputs",
    "constraints",
    "evidence",
    "acceptance",
    "time",
    "authority",
)


@dataclass(frozen=True)
class PrecisionFinding:
    code: str
    field: str
    value: str
    reason: str


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def scan_text(text: str, field: str = "intent") -> list[PrecisionFinding]:
    lowered = text.casefold()
    findings: list[PrecisionFinding] = []
    for term in VAGUE_TERMS:
        if re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", lowered):
            findings.append(
                PrecisionFinding(
                    code="VAGUE_TERM",
                    field=field,
                    value=term,
                    reason="replace with an observable, bounded specification",
                )
            )
    if "something" in lowered or "anything" in lowered or "somehow" in lowered:
        findings.append(
            PrecisionFinding(
                code="UNBOUND_REFERENCE",
                field=field,
                value="something/anything/somehow",
                reason="name the concrete object, mechanism, or allowed alternatives",
            )
        )
    return sorted(findings, key=lambda row: (row.field, row.value))


def validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
    findings: list[PrecisionFinding] = []
    for field in REQUIRED_FIELDS:
        value = spec.get(field)
        if value in (None, "", [], {}):
            findings.append(
                PrecisionFinding(
                    code="MISSING_FIELD",
                    field=field,
                    value="",
                    reason="required for executable interpretation",
                )
            )

    text_fields = ("subject", "action", "scope", "constraints", "acceptance")
    for field in text_fields:
        value = spec.get(field)
        if isinstance(value, str):
            findings.extend(scan_text(value, field))

    acceptance = spec.get("acceptance")
    if isinstance(acceptance, str) and not re.search(r"\d|equals|contains|must |exit code|hash|status|present|absent", acceptance, re.I):
        findings.append(
            PrecisionFinding(
                code="NON_TESTABLE_ACCEPTANCE",
                field="acceptance",
                value=acceptance,
                reason="state a condition a verifier can deterministically inspect",
            )
        )

    result = {
        "schema": "evez-precision-v1",
        "valid": not findings,
        "required_fields": list(REQUIRED_FIELDS),
        "findings": [asdict(row) for row in findings],
        "spec_sha256": None,
    }
    result["spec_sha256"] = digest(result)
    return result


def compile_from_intent(intent: str) -> dict[str, Any]:
    findings = scan_text(intent)
    result = {
        "schema": "evez-precision-intent-v1",
        "intent": intent,
        "vague_terms": [asdict(row) for row in findings],
        "status": "REQUIRES_SPECIFICATION" if findings else "PRECISE_ENOUGH_FOR_DECOMPOSITION",
    }
    result["intent_sha256"] = digest(result)
    return result
