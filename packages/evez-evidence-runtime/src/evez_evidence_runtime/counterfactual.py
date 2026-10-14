"""Counterfactual test contracts without pretending to simulate reality."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True)
class Counterfactual:
    hypothesis: str
    expected: Callable[[dict[str, Any]], bool]
    label: str

@dataclass(frozen=True)
class CounterfactualResult:
    label: str
    hypothesis: str
    matched: bool

class CounterfactualEngine:
    def compare(self, observation: dict[str, Any], cases: list[Counterfactual]) -> list[CounterfactualResult]:
        return [CounterfactualResult(c.label, c.hypothesis, bool(c.expected(observation))) for c in cases]
