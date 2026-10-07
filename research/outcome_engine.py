#!/usr/bin/env python3
"""Compile natural-language intent into a bounded, testable outcome contract."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class OutcomeSpec:
    outcome_id: str
    intent: str
    objective: str
    acceptance_criteria: tuple[str, ...]
    stages: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    action_class: str
    requires_authorization: bool

    def validate(self) -> None:
        if not self.outcome_id or not self.intent or not self.objective:
            raise ValueError("outcome identity is incomplete")
        if not self.acceptance_criteria:
            raise ValueError("acceptance criteria are required")
        if self.action_class not in {"READ", "BUILD", "VERIFY", "COMMUNICATE", "CONSEQUENTIAL"}:
            raise ValueError("invalid action class")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def normalize_intent(text: str) -> str:
    value = " ".join(text.split()).strip()
    if not value:
        raise ValueError("intent cannot be empty")
    return value


def classify_action(intent: str) -> str:
    lowered = intent.lower()
    if any(word in lowered for word in ("deploy", "merge", "delete", "publish", "send", "purchase", "fund")):
        return "CONSEQUENTIAL"
    if any(word in lowered for word in ("reach", "notify", "message", "contact")):
        return "COMMUNICATE"
    if any(word in lowered for word in ("test", "verify", "audit", "check")):
        return "VERIFY"
    if any(word in lowered for word in ("build", "create", "implement", "make", "fix", "finish")):
        return "BUILD"
    return "READ"


def compile_outcome(text: str) -> dict[str, Any]:
    intent = normalize_intent(text)
    action = classify_action(intent)
    objective = re.split(r"[.!?]\s+|\n+", intent)[0]
    stages = ("PARSE", "EXTRACT", "MAP", "DERIVE", "BUILD", "TEST", "VERIFY", "PACKAGE")
    criteria = (
        "implementation exists",
        "deterministic tests pass",
        "provenance is preserved",
        "unsupported capabilities remain UNKNOWN",
        "verification boundary is explicit",
    )
    stop = (
        "required evidence is unavailable",
        "a consequential action lacks authorization",
        "verification fails",
    )
    result = {
        "schema": "evez-outcome-v1",
        "outcome": asdict(
            OutcomeSpec(
                outcome_id=digest({"intent": intent})[:16],
                intent=intent,
                objective=objective,
                acceptance_criteria=criteria,
                stages=stages,
                stop_conditions=stop,
                action_class=action,
                requires_authorization=action == "CONSEQUENTIAL",
            )
        ),
    }
    result["outcome_sha256"] = digest(result)
    return result
