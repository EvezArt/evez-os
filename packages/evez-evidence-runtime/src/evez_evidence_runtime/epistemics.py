"""Guards against unsupported epistemic promotion and broken claim lineage."""
from __future__ import annotations
from dataclasses import dataclass, field
from .ontology import EpistemicState

@dataclass(frozen=True)
class Falsifier:
    falsifier_id: str
    description: str
    observable: str

@dataclass
class ClaimLineage:
    claim_id: str
    claim: str
    source_observations: list[str] = field(default_factory=list)
    source_witnesses: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    falsifiers: list[Falsifier] = field(default_factory=list)
    state: EpistemicState = EpistemicState.PROPOSED

    def add_falsifier(self, falsifier: Falsifier) -> None:
        self.falsifiers.append(falsifier)

    def can_promote(self, target: EpistemicState, *, new_evidence: bool) -> bool:
        if target == EpistemicState.VERIFIED:
            return bool(
                new_evidence
                and self.source_observations
                and self.tests
                and self.falsifiers
                and not self.contradictions
            )
        if target == EpistemicState.SUPPORTED:
            return bool(new_evidence and (self.source_observations or self.tests))
        if target == EpistemicState.UNKNOWN:
            return True
        return target in {
            EpistemicState.PROPOSED,
            EpistemicState.INFERRED,
            EpistemicState.STALE,
            EpistemicState.CONTRADICTED,
            EpistemicState.RETRACTED,
        }

@dataclass(frozen=True)
class PromotionResult:
    allowed: bool
    previous: EpistemicState
    requested: EpistemicState
    reason: str

def promote(lineage: ClaimLineage, target: EpistemicState, *, new_evidence: bool) -> PromotionResult:
    if lineage.can_promote(target, new_evidence=new_evidence):
        previous = lineage.state
        lineage.state = target
        return PromotionResult(True, previous, target, "promotion contract satisfied")
    return PromotionResult(
        False,
        lineage.state,
        target,
        "promotion would create epistemic strength without sufficient evidence",
    )

def epistemic_conservation_violation(
    previous: EpistemicState,
    target: EpistemicState,
    *,
    new_evidence: bool,
) -> bool:
    order = {
        EpistemicState.UNKNOWN: 0,
        EpistemicState.PROPOSED: 1,
        EpistemicState.INFERRED: 2,
        EpistemicState.SUPPORTED: 3,
        EpistemicState.VERIFIED: 4,
    }
    return (
        target in order
        and previous in order
        and order[target] > order[previous]
        and not new_evidence
    )
