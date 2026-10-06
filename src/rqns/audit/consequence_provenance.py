"""Evidence-bound consequence provenance for recursive agent execution.

This module tracks what an observable outcome changed about the future search
space. It does not infer hidden model state or attacker intent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Iterable, Optional


@dataclass(frozen=True)
class ConsequenceOutcome:
    outcome_id: str
    parent_outcome_id: Optional[str]
    observation: str
    enabled: tuple[str, ...] = ()
    constrained: tuple[str, ...] = ()
    falsified: tuple[str, ...] = ()
    next_tests: tuple[str, ...] = ()
    representation_change: Optional[str] = None
    independent_observation_ref: Optional[str] = None
    status: str = "PROPOSED"

    def canonical_bytes(self) -> bytes:
        payload = {
            "outcome_id": self.outcome_id,
            "parent_outcome_id": self.parent_outcome_id,
            "observation": self.observation,
            "enabled": list(self.enabled),
            "constrained": list(self.constrained),
            "falsified": list(self.falsified),
            "next_tests": list(self.next_tests),
            "representation_change": self.representation_change,
            "independent_observation_ref": self.independent_observation_ref,
            "status": self.status,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass
class ConsequenceLedger:
    outcomes: list[ConsequenceOutcome] = field(default_factory=list)

    def append(self, outcome: ConsequenceOutcome) -> str:
        if self.outcomes and outcome.parent_outcome_id != self.outcomes[-1].outcome_id:
            raise ValueError("outcome parent must reference the current lineage tip")
        if outcome.status == "VERIFIED" and not outcome.independent_observation_ref:
            raise ValueError("VERIFIED consequence requires independent observation")
        self.outcomes.append(outcome)
        return outcome.content_hash()

    def consequence_depth(self, outcome_id: str) -> int:
        by_id = {item.outcome_id: item for item in self.outcomes}
        depth = 0
        current = by_id.get(outcome_id)
        while current is not None and current.parent_outcome_id is not None:
            depth += 1
            current = by_id.get(current.parent_outcome_id)
        return depth

    def live_outcomes(self) -> list[ConsequenceOutcome]:
        return [
            item for item in self.outcomes
            if item.enabled or item.constrained or item.falsified or item.next_tests
            or item.representation_change
        ]

    def max_live_depth(self) -> int:
        live_ids = {item.outcome_id for item in self.live_outcomes()}
        return max((self.consequence_depth(item_id) for item_id in live_ids), default=0)

    def snapshot_hash(self) -> str:
        payload = [item.canonical_bytes().decode() for item in self.outcomes]
        return hashlib.sha256("\n".join(payload).encode()).hexdigest()

    def export_jsonl(self) -> str:
        return "\n".join(
            item.canonical_bytes().decode() for item in self.outcomes
        )


@dataclass(frozen=True)
class ConsequencePrediction:
    source_outcome_id: str
    predicted_transition: str
    falsifier: str
    test_ref: str

    def canonical_bytes(self) -> bytes:
        payload = {
            "source_outcome_id": self.source_outcome_id,
            "predicted_transition": self.predicted_transition,
            "falsifier": self.falsifier,
            "test_ref": self.test_ref,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def consequence_delta(before: ConsequenceOutcome, after: ConsequenceOutcome) -> dict[str, tuple[str, ...]]:
    return {
        "enabled": tuple(sorted(set(after.enabled) - set(before.enabled))),
        "constrained": tuple(sorted(set(after.constrained) - set(before.constrained))),
        "falsified": tuple(sorted(set(after.falsified) - set(before.falsified))),
        "next_tests": tuple(sorted(set(after.next_tests) - set(before.next_tests))),
    }
