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


class RecoveryCatalog:
    """Generate conservative standard alternatives without granting execution authority."""

    @staticmethod
    def for_failure(failure_class: FailureClass) -> tuple[RecoveryAlternative, ...]:
        common = {
            "safe": True, "authorized": True, "observable": True, "reversible": True,
            "idempotent": True, "compensatable": False, "cost": 1.0, "risk": 0.1,
            "information_gain": 1.0, "blast_radius": 0.1,
        }
        if failure_class == FailureClass.TRANSIENT:
            return (
                RecoveryAlternative(
                    action_id="bounded-retry", description="Retry within a finite budget.",
                    failure_classes=frozenset({failure_class}), retryable=True,
                    expected_observation="same dependency succeeds", **common
                ),
                RecoveryAlternative(
                    action_id="half-open-probe", description="Probe dependency recovery before reopening traffic.",
                    failure_classes=frozenset({failure_class}), expected_observation="probe succeeds",
                    cost=0.5, information_gain=2.0, **{k: v for k, v in common.items() if k not in {"cost", "information_gain"}}
                ),
                RecoveryAlternative(
                    action_id="defer", description="Defer execution without asserting recovery.",
                    failure_classes=frozenset({failure_class}), reversible=True,
                    expected_observation="work remains queued", cost=0.2, risk=0.0,
                    information_gain=1.0, blast_radius=0.0, safe=True, authorized=True,
                    observable=True, idempotent=True, compensatable=False
                ),
            )
        if failure_class == FailureClass.CAPACITY:
            return (
                RecoveryAlternative(
                    action_id="backpressure", description="Reduce intake and preserve bounded work.",
                    failure_classes=frozenset({failure_class}), expected_observation="load decreases",
                    **common
                ),
                RecoveryAlternative(
                    action_id="defer", description="Defer work instead of exceeding capacity.",
                    failure_classes=frozenset({failure_class}), expected_observation="work remains queued",
                    cost=0.2, risk=0.0, information_gain=1.0, blast_radius=0.0,
                    safe=True, authorized=True, observable=True, reversible=True,
                    idempotent=True, compensatable=False
                ),
            )
        if failure_class == FailureClass.INTEGRITY:
            return (
                RecoveryAlternative(
                    action_id="quarantine", description="Isolate suspect state while preserving evidence.",
                    failure_classes=frozenset({failure_class}), expected_observation="suspect state isolated",
                    reversible=True, idempotent=True, compensatable=False, safe=True, authorized=True,
                    observable=True, cost=1.0, risk=0.0, information_gain=4.0, blast_radius=0.0
                ),
                RecoveryAlternative(
                    action_id="reconcile", description="Reconcile conflicting state against preserved evidence.",
                    failure_classes=frozenset({failure_class}), expected_observation="conflict resolved or remains explicit",
                    reversible=True, idempotent=True, compensatable=True, compensation="restore prior known-good state",
                    safe=True, authorized=True, observable=True, cost=3.0, risk=0.2,
                    information_gain=5.0, blast_radius=0.2
                ),
            )
        if failure_class == FailureClass.AUTHORIZATION:
            return (
                RecoveryAlternative(
                    action_id="deny-and-witness", description="Deny the unauthorized action and preserve the attempt as evidence.",
                    failure_classes=frozenset({failure_class}), expected_observation="unauthorized action blocked",
                    reversible=True, idempotent=True, compensatable=False, safe=True, authorized=True,
                    observable=True, cost=0.1, risk=0.0, information_gain=3.0, blast_radius=0.0
                ),
                RecoveryAlternative(
                    action_id="human-review", description="Escalate for explicit authority adjudication.",
                    failure_classes=frozenset({failure_class}), requires_human=True,
                    expected_observation="human authority decision recorded",
                    reversible=True, idempotent=True, compensatable=False, safe=True, authorized=True,
                    observable=True, cost=2.0, risk=0.1, information_gain=4.0, blast_radius=0.1
                ),
            )
        if failure_class == FailureClass.UNKNOWN:
            return (
                RecoveryAlternative(
                    action_id="discriminating-probe", description="Collect evidence that separates competing failure hypotheses.",
                    failure_classes=frozenset({FailureClass.UNKNOWN}), expected_observation="hypothesis set narrows",
                    reversible=True, idempotent=True, compensatable=False, safe=True, authorized=True,
                    observable=True, cost=1.0, risk=0.0, information_gain=5.0, blast_radius=0.0
                ),
            )
        return (
            RecoveryAlternative(
                action_id="quarantine", description="Isolate the failure without claiming recovery.",
                failure_classes=frozenset({failure_class}), expected_observation="failure isolated",
                reversible=True, idempotent=True, compensatable=False, safe=True, authorized=True,
                observable=True, cost=1.0, risk=0.0, information_gain=2.0, blast_radius=0.0
            ),
        )


@dataclass(frozen=True)
class RecoveryWitness:
    failure_id: str
    decision: RecoveryDecision
    selected_alternative: RecoveryAlternative | None


class RecoveryCoordinator:
    """Plans and witnesses recovery transitions; it never executes external effects."""

    def __init__(self, *, engine: RecoveryEngine | None = None, spine=None) -> None:
        self.engine = engine or RecoveryEngine()
        self.spine = spine

    def plan(self, *, failure_id: str, failure_class: FailureClass, alternatives: Iterable[RecoveryAlternative] | None = None, allow_human: bool = False) -> RecoveryWitness:
        candidates = tuple(alternatives) if alternatives is not None else RecoveryCatalog.for_failure(failure_class)
        decision = self.engine.plan(
            failure_id=failure_id,
            failure_class=failure_class,
            alternatives=candidates,
            allow_human=allow_human,
        )
        selected = next((a for a in candidates if a.action_id == decision.selected), None)
        if self.spine is not None:
            self.spine.append("recovery_planned", {
                "failure_id": failure_id,
                "failure_class": failure_class.value,
                "selected": decision.selected,
                "ranked": list(decision.ranked),
                "rejected": decision.rejected,
                "state": decision.state.value,
            })
        return RecoveryWitness(failure_id, decision, selected)

    def attempt(self, *, witness: RecoveryWitness) -> bool:
        allowed = witness.decision.selected is not None and self.engine.begin_attempt()
        if self.spine is not None:
            self.spine.append("recovery_attempt", {
                "failure_id": witness.failure_id,
                "action_id": witness.decision.selected,
                "allowed": allowed,
            })
        return allowed

    def observe(self, *, witness: RecoveryWitness, expected: bool, observed: bool, contradictory: bool = False, observation: str = "") -> RecoveryReceipt:
        state = self.engine.classify_observation(expected=expected, observed=observed, contradictory=contradictory)
        receipt = self.engine.receipt(
            failure_id=witness.failure_id,
            action_id=witness.decision.selected,
            failure_class=witness.selected_alternative.failure_classes.pop() if witness.selected_alternative else FailureClass.UNKNOWN,
            state=state,
            observation=observation,
            compensation=witness.selected_alternative.compensation if witness.selected_alternative else None,
        )
        if self.spine is not None:
            self.spine.append("recovery_outcome", {
                "failure_id": receipt.failure_id,
                "action_id": receipt.action_id,
                "failure_class": receipt.failure_class.value,
                "state": receipt.state.value,
                "observation": receipt.observation,
                "compensation": receipt.compensation,
                "evidence_pending": receipt.evidence_pending,
            })
        return receipt
