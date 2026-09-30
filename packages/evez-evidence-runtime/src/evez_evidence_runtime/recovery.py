"""Bounded recovery planning for failed runtime operations.

Recovery is evidence-constrained action selection, not blind retry logic.
All actions are synthetic/declared by the caller. This module never executes
an external side effect itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class FailureClass(str, Enum):
    TRANSIENT = "TRANSIENT"
    PERSISTENT = "PERSISTENT"
    CAPACITY = "CAPACITY"
    DEPENDENCY = "DEPENDENCY"
    AUTHORIZATION = "AUTHORIZATION"
    INTEGRITY = "INTEGRITY"
    CONFIGURATION = "CONFIGURATION"
    DEPLOYMENT = "DEPLOYMENT"
    PROVENANCE = "PROVENANCE"
    ADVERSARIAL = "ADVERSARIAL"
    UNKNOWN = "UNKNOWN"


class RecoveryState(str, Enum):
    OBSERVED_FAILURE = "OBSERVED_FAILURE"
    CLASSIFIED = "CLASSIFIED"
    ALTERNATIVES_GENERATED = "ALTERNATIVES_GENERATED"
    ALTERNATIVES_FILTERED = "ALTERNATIVES_FILTERED"
    RECOVERY_SELECTED = "RECOVERY_SELECTED"
    EXECUTING = "EXECUTING"
    VERIFIED_RECOVERY = "VERIFIED_RECOVERY"
    NEXT_ALTERNATIVE = "NEXT_ALTERNATIVE"
    CAIN = "CAIN"
    REJECTED = "REJECTED"
    EVIDENCE_PENDING = "EVIDENCE_PENDING"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class RecoveryAlternative:
    action_id: str
    description: str
    failure_classes: frozenset[FailureClass]
    safe: bool
    authorized: bool
    observable: bool
    reversible: bool
    idempotent: bool
    compensatable: bool
    cost: float
    risk: float
    information_gain: float
    blast_radius: float
    retryable: bool = False
    requires_human: bool = False
    preconditions: frozenset[str] = frozenset()
    expected_observation: str = ""
    compensation: str | None = None


@dataclass(frozen=True)
class RecoveryDecision:
    selected: str | None
    rejected: dict[str, str]
    ranked: tuple[str, ...]
    state: RecoveryState
    rationale: tuple[str, ...]


@dataclass(frozen=True)
class RecoveryReceipt:
    failure_id: str
    action_id: str | None
    failure_class: FailureClass
    state: RecoveryState
    observation: str
    compensation: str | None
    evidence_pending: bool


class RecoveryBudget:
    def __init__(self, *, max_attempts: int = 3, max_risk: float = 1.0, max_blast_radius: float = 1.0) -> None:
        self.max_attempts = max_attempts
        self.max_risk = max_risk
        self.max_blast_radius = max_blast_radius
        self.attempts = 0

    def consume(self) -> bool:
        if self.attempts >= self.max_attempts:
            return False
        self.attempts += 1
        return True


class RecoveryEngine:
    """Selects a bounded recovery alternative; never performs the action."""

    def __init__(self, *, budget: RecoveryBudget | None = None) -> None:
        self.budget = budget or RecoveryBudget()

    @staticmethod
    def _eligible(a: RecoveryAlternative, failure_class: FailureClass, *, allow_human: bool) -> tuple[bool, str]:
        if failure_class not in a.failure_classes and FailureClass.UNKNOWN not in a.failure_classes:
            return False, "failure-class-mismatch"
        if not a.safe:
            return False, "unsafe"
        if not a.authorized:
            return False, "unauthorized"
        if not a.observable:
            return False, "no-observable"
        if a.cost < 0 or a.risk < 0 or a.blast_radius < 0:
            return False, "invalid-negative-budget"
        if a.retryable and not a.idempotent and not a.compensatable:
            return False, "retry-without-idempotency-or-compensation"
        if a.requires_human and not allow_human:
            return False, "human-review-required"
        return True, ""

    @staticmethod
    def _dominates(a: RecoveryAlternative, b: RecoveryAlternative) -> bool:
        return (
            a.cost <= b.cost
            and a.risk <= b.risk
            and a.blast_radius <= b.blast_radius
            and a.information_gain >= b.information_gain
            and (a.cost < b.cost or a.risk < b.risk or a.blast_radius < b.blast_radius or a.information_gain > b.information_gain)
        )

    def plan(
        self,
        *,
        failure_id: str,
        failure_class: FailureClass,
        alternatives: Iterable[RecoveryAlternative],
        allow_human: bool = False,
    ) -> RecoveryDecision:
        items = list(alternatives)
        rejected: dict[str, str] = {}
        eligible: list[RecoveryAlternative] = []
        for a in items:
            ok, reason = self._eligible(a, failure_class, allow_human=allow_human)
            if ok and (a.risk > self.budget.max_risk or a.blast_radius > self.budget.max_blast_radius):
                ok, reason = False, "budget-exceeded"
            if ok:
                eligible.append(a)
            else:
                rejected[a.action_id] = reason

        survivors: list[RecoveryAlternative] = []
        for a in eligible:
            if any(b.action_id != a.action_id and self._dominates(b, a) for b in eligible):
                rejected[a.action_id] = "dominated"
            else:
                survivors.append(a)

        survivors.sort(
            key=lambda a: (
                a.information_gain / max(a.cost, 1e-12),
                -a.risk,
                -a.blast_radius,
                int(a.reversible),
                a.action_id,
            ),
            reverse=True,
        )
        ranked = tuple(a.action_id for a in survivors)
        if not survivors:
            return RecoveryDecision(
                None, rejected, ranked, RecoveryState.CAIN if failure_class == FailureClass.INTEGRITY else RecoveryState.QUARANTINED,
                ("No admissible recovery alternative remains.", "Preserve the failure as evidence; do not manufacture success."),
            )
        return RecoveryDecision(
            survivors[0].action_id, rejected, ranked, RecoveryState.RECOVERY_SELECTED,
            ("Safety, authority, observability, and budget gates passed.", "Recovery selection is not recovery execution.",),
        )

    def begin_attempt(self) -> bool:
        return self.budget.consume()

    @staticmethod
    def classify_observation(*, expected: bool, observed: bool, contradictory: bool = False) -> RecoveryState:
        if contradictory:
            return RecoveryState.CAIN
        if expected and observed:
            return RecoveryState.VERIFIED_RECOVERY
        if not observed:
            return RecoveryState.NEXT_ALTERNATIVE
        return RecoveryState.EVIDENCE_PENDING

    @staticmethod
    def receipt(
        *,
        failure_id: str,
        action_id: str | None,
        failure_class: FailureClass,
        state: RecoveryState,
        observation: str,
        compensation: str | None = None,
    ) -> RecoveryReceipt:
        return RecoveryReceipt(
            failure_id=failure_id,
            action_id=action_id,
            failure_class=failure_class,
            state=state,
            observation=observation,
            compensation=compensation,
            evidence_pending=state in {RecoveryState.EVIDENCE_PENDING, RecoveryState.CAIN},
        )
