"""Evidence-bound allocation across unresolved residuals.

This module treats attention/computation as an auditable resource allocation
problem. Scores prioritize investigations; they are not truth probabilities.
Representational tunneling records frame changes instead of treating them as
self-justifying leaps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Dict, Iterable, List, Mapping, Tuple


@dataclass(frozen=True)
class Investigation:
    investigation_id: str
    residual_id: str
    unexplained: float
    reproducibility: float
    recurrence: float
    predicted_information_gain: float
    cost: float
    assumption_burden: float
    falsifiability: float
    evidence_quality: float

    def allocation_score(self) -> float:
        numerator = (
            self.unexplained
            * self.reproducibility
            * self.recurrence
            * self.predicted_information_gain
            * self.falsifiability
            * self.evidence_quality
        )
        return numerator / ((self.cost + 1.0) * (self.assumption_burden + 1.0))


@dataclass(frozen=True)
class RepresentationTransition:
    transition_id: str
    residual_id: str
    from_frame: str
    to_frame: str
    trigger: str
    expected_distinction: str
    test_ref: str
    status: str = "PROPOSED"

    def canonical_bytes(self) -> bytes:
        return json.dumps(
            self.__dict__, sort_keys=True, separators=(",", ":")
        ).encode()

    def content_hash(self) -> str:
        return sha256(self.canonical_bytes()).hexdigest()


@dataclass
class AllocationLedger:
    decisions: List[Tuple[str, float]] = field(default_factory=list)
    transitions: List[RepresentationTransition] = field(default_factory=list)

    def allocate(self, investigations: Iterable[Investigation]) -> List[Tuple[str, float]]:
        ranked = sorted(
            ((item.investigation_id, item.allocation_score()) for item in investigations),
            key=lambda pair: (-pair[1], pair[0]),
        )
        self.decisions.extend(ranked)
        return ranked

    def record_transition(self, transition: RepresentationTransition) -> str:
        self.transitions.append(transition)
        return transition.content_hash()

    def audit_transition(self, transition_id: str) -> bool:
        for transition in self.transitions:
            if transition.transition_id == transition_id:
                return bool(
                    transition.from_frame
                    and transition.to_frame
                    and transition.trigger
                    and transition.expected_distinction
                    and transition.test_ref
                )
        return False


__all__ = ["AllocationLedger", "Investigation", "RepresentationTransition"]
