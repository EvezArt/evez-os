"""Deterministic experiment selection and epistemic optimization primitives.

This module deliberately avoids a single confidence score. It selects tests by
hard safety/observability constraints, then by information value, contradiction
resolution, reproducibility, and cost.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable
from .dependencies import DependencyGraph
from .ontology import EpistemicState

@dataclass(frozen=True)
class CandidateTest:
    test_id: str
    description: str
    information_gain: float
    contradiction_resolution: float
    reproducibility: float
    cost: float
    risk: float
    discriminates: bool
    observable: bool
    safe: bool
    affects_claim: bool
    dependencies: frozenset[str] = frozenset()
    falsifiers: frozenset[str] = frozenset()

@dataclass(frozen=True)
class OptimizationDecision:
    selected: str | None
    rejected: dict[str, str]
    ranked: tuple[str, ...]
    bottlenecks: tuple[str, ...]
    saturation: str
    rationale: tuple[str, ...]

@dataclass
class TestSelector:
    max_risk: float = 1.0
    min_information_gain: float = 0.0
    min_reproducibility: float = 0.0

    def _eligible(self, t: CandidateTest) -> tuple[bool, str]:
        if not t.safe:
            return False, "unsafe"
        if not t.observable:
            return False, "no-observable"
        if not t.discriminates:
            return False, "non-discriminating"
        if not t.affects_claim:
            return False, "does-not-affect-claim"
        if t.risk > self.max_risk:
            return False, "risk-budget-exceeded"
        if t.information_gain < self.min_information_gain:
            return False, "insufficient-information-gain"
        if t.reproducibility < self.min_reproducibility:
            return False, "insufficient-reproducibility"
        if t.cost < 0 or t.risk < 0:
            return False, "invalid-negative-cost-or-risk"
        return True, ""

    @staticmethod
    def _dominates(a: CandidateTest, b: CandidateTest) -> bool:
        return (
            a.cost <= b.cost
            and a.risk <= b.risk
            and a.information_gain >= b.information_gain
            and a.reproducibility >= b.reproducibility
            and a.contradiction_resolution >= b.contradiction_resolution
            and (
                a.cost < b.cost
                or a.risk < b.risk
                or a.information_gain > b.information_gain
                or a.reproducibility > b.reproducibility
                or a.contradiction_resolution > b.contradiction_resolution
            )
        )

    def select(
        self,
        candidates: Iterable[CandidateTest],
        *,
        graph: DependencyGraph | None = None,
        uncertain: set[str] | None = None,
    ) -> OptimizationDecision:
        items = list(candidates)
        rejected: dict[str, str] = {}
        eligible: list[CandidateTest] = []
        for item in items:
            ok, reason = self._eligible(item)
            if ok:
                eligible.append(item)
            else:
                rejected[item.test_id] = reason

        # Remove dominated experiments before ranking. This keeps the optimizer
        # from spending budget on a strictly worse test.
        survivors: list[CandidateTest] = []
        for item in eligible:
            if any(other.test_id != item.test_id and self._dominates(other, item) for other in eligible):
                rejected[item.test_id] = "dominated"
            else:
                survivors.append(item)

        def key(t: CandidateTest) -> tuple[float, float, float, float, float, str]:
            ratio = t.information_gain / max(t.cost, 1e-12)
            return (
                t.contradiction_resolution,
                ratio,
                t.information_gain,
                t.reproducibility,
                -t.risk,
                t.test_id,
            )

        survivors.sort(key=key, reverse=True)
        ranked = tuple(t.test_id for t in survivors)

        bottlenecks: tuple[str, ...] = ()
        if graph is not None and uncertain:
            debt = graph.epistemic_debt(uncertain)
            bottlenecks = tuple(
                node for node, count in sorted(debt.items(), key=lambda kv: (-kv[1], kv[0]))
                if count > 0
            )

        if not survivors:
            saturation = "SATURATED" if items else "BLOCKED"
            rationale = ("No eligible discriminating experiment remains.",)
            return OptimizationDecision(None, rejected, ranked, bottlenecks, saturation, rationale)

        selected = survivors[0]
        saturation = "CONVERGING" if len(survivors) > 1 else "ACTIVE"
        rationale = (
            "Selected after safety and observability gates.",
            "Dominated experiments were removed.",
            "Ranking prioritizes contradiction resolution, information/cost, reproducibility, then risk.",
        )
        return OptimizationDecision(selected.test_id, rejected, ranked, bottlenecks, saturation, rationale)


def claim_state_transition(classification: str) -> EpistemicState:
    """Map a runtime result without promoting UNKNOWN or PASS to VERIFIED."""
    return {
        "PASS": EpistemicState.SUPPORTED,
        "VIOLATION": EpistemicState.CONTRADICTED,
        "CONTRADICTION": EpistemicState.CONTRADICTED,
        "UNKNOWN": EpistemicState.UNKNOWN,
    }.get(classification, EpistemicState.UNKNOWN)
