"""Universal map reconciliation: evidence-backed state, failure, and next action.

This module only consumes structured observations and emits a reconciliation
record. It does not probe external systems or perform side effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .decision import NextAction, OperationalDecision, OperationalPlanner
from .failure import FailureClassifier, FailureObservation
from .maps import MapSpec, UniversalMapRegistry
from .epistemics import ClaimLineage


class ReconciliationState(str, Enum):
    OBSERVED = "OBSERVED"
    EVIDENCE_PENDING = "EVIDENCE_PENDING"
    ACTIONABLE = "ACTIONABLE"
    VERIFIED = "VERIFIED"
    CONTRADICTED = "CONTRADICTED"


@dataclass(frozen=True)
class MapReconciliation:
    map_id: str
    target: str
    observed_state: str
    epistemic_state: str
    failure_class: str
    next_action: str
    selected_id: str | None
    evidence_ids: tuple[str, ...]
    rationale: tuple[str, ...]


class MapReconciler:
    """Reconcile a registered map surface from supplied evidence only."""

    def __init__(self, registry: UniversalMapRegistry, planner: OperationalPlanner | None = None) -> None:
        self.registry = registry
        self.planner = planner or OperationalPlanner()
        self.classifier = FailureClassifier()

    def reconcile(
        self,
        *,
        map_id: str,
        lineage: ClaimLineage,
        observation: FailureObservation | None = None,
        observed_state: str = "UNKNOWN",
        evidence_ids: Iterable[str] = (),
    ) -> MapReconciliation:
        spec = self.registry.get(map_id)
        evidence = tuple(evidence_ids)
        classification = self.classifier.classify(observation or FailureObservation())
        decision = self.planner.decide_from_observation(
            lineage=lineage,
            observation=observation or FailureObservation(),
        )
        return MapReconciliation(
            map_id=spec.map_id,
            target=spec.target,
            observed_state=observed_state,
            epistemic_state=lineage.state.value,
            failure_class=classification.failure_class.value,
            next_action=decision.action.value,
            selected_id=decision.selected_id,
            evidence_ids=evidence,
            rationale=classification.rationale + (decision.reason,),
        )

    def reconcile_many(
        self,
        observations: Iterable[tuple[str, ClaimLineage, FailureObservation | None, str, Iterable[str]]],
    ) -> tuple[MapReconciliation, ...]:
        return tuple(
            self.reconcile(
                map_id=map_id,
                lineage=lineage,
                observation=observation,
                observed_state=observed_state,
                evidence_ids=evidence_ids,
            )
            for map_id, lineage, observation, observed_state, evidence_ids in observations
        )
