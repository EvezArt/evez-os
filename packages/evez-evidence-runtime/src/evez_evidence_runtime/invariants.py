"""Typed invariant battery with explicit PASS/FAIL/ERROR outcomes."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any

State = dict[str, Any]
Predicate = Callable[[State], bool]

@dataclass(frozen=True)
class Invariant:
    name: str
    predicate: Predicate
    description: str

@dataclass(frozen=True)
class InvariantResult:
    name: str
    passed: bool
    error: str | None = None

class InvariantBattery:
    def __init__(self, invariants: list[Invariant] | None = None) -> None:
        self.invariants = list(invariants or [])

    def add(self, invariant: Invariant) -> None:
        if any(x.name == invariant.name for x in self.invariants):
            raise ValueError(f"duplicate invariant: {invariant.name}")
        self.invariants.append(invariant)

    def check(self, state: State) -> list[InvariantResult]:
        results: list[InvariantResult] = []
        for invariant in self.invariants:
            try:
                results.append(InvariantResult(invariant.name, bool(invariant.predicate(dict(state)))))
            except Exception as exc:
                results.append(InvariantResult(invariant.name, False, str(exc)))
        return results

    @staticmethod
    def all_hold(results: list[InvariantResult]) -> bool:
        return all(result.passed for result in results)

def authorization_battery() -> InvariantBattery:
    return InvariantBattery([
        Invariant(
            "actual_action_subset_of_authorized",
            lambda s: s.get("actual_action") == s.get("authorized_action"),
            "The synthetic action actually executed must equal an explicitly authorized action.",
        ),
        Invariant(
            "recorded_action_matches_actual",
            lambda s: s.get("recorded_action") == s.get("actual_action"),
            "The witness record must match the synthetic action actually executed.",
        ),
    ])
