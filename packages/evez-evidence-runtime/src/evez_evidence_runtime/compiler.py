"""Claim-to-test compiler."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class TestPlan:
    claim: str
    terms: tuple[str, ...]
    observables: tuple[str, ...]
    required_evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim": self.claim,
            "terms": self.terms,
            "observables": self.observables,
            "required_evidence": self.required_evidence,
        }

class ClaimCompiler:
    def compile(self, claim: str, *, observables: list[str], required_evidence: list[str]) -> TestPlan:
        normalized = claim.strip()
        if not normalized:
            raise ValueError("claim is required")
        terms = tuple(sorted({w.strip(".,:;()[]{}").lower() for w in normalized.split() if w.strip()}))
        return TestPlan(normalized, terms, tuple(observables), tuple(required_evidence))
