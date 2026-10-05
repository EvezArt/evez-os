"""Adaptive control algorithms for anti-influence containment.

These controls govern when an investigating unit should remain in observation
mode, escalate to independent challenge, or enter lockdown. They do not infer
truth from persuasion signals. They only constrain exposure and authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
from typing import Iterable, Mapping, Sequence

from .anti_influence import (
    EvidenceEnvelope,
    InfluenceAssessment,
    InfluenceSignals,
)


class ContainmentState(str, Enum):
    OPEN = "OPEN"
    CAUTION = "CAUTION"
    ESCALATE = "ESCALATE"
    LOCKDOWN = "LOCKDOWN"


@dataclass(frozen=True)
class ExposureBudget:
    total_limit: float = 2.0
    source_limit: float = 0.75


@dataclass(frozen=True)
class ExposureDecision:
    admitted: bool
    state: ContainmentState
    cumulative_score: float
    source_score: float
    reason: str


class ExposureController:
    """Monotonic exposure accounting with per-source and global ceilings."""

    def __init__(self, budget: ExposureBudget | None = None) -> None:
        self.budget = budget or ExposureBudget()
        if self.budget.total_limit <= 0 or self.budget.source_limit <= 0:
            raise ValueError("exposure limits must be positive")
        self._total = 0.0
        self._sources: dict[str, float] = {}

    @property
    def total(self) -> float:
        return self._total

    def admit(self, source_id: str, assessment: InfluenceAssessment) -> ExposureDecision:
        if not source_id.strip():
            raise ValueError("source_id is required")
        score = max(0.0, min(1.0, assessment.score))
        next_total = self._total + score
        next_source = self._sources.get(source_id, 0.0) + score

        if next_total > self.budget.total_limit:
            return ExposureDecision(
                False,
                ContainmentState.LOCKDOWN,
                self._total,
                self._sources.get(source_id, 0.0),
                "global influence exposure budget exceeded",
            )

        if next_source > self.budget.source_limit:
            return ExposureDecision(
                False,
                ContainmentState.ESCALATE,
                self._total,
                self._sources.get(source_id, 0.0),
                "per-source influence exposure budget exceeded",
            )

        self._total = next_total
        self._sources[source_id] = next_source
        state = (
            ContainmentState.ESCALATE
            if assessment.quarantine_recommended
            else ContainmentState.CAUTION
            if assessment.score >= 0.30
            else ContainmentState.OPEN
        )
        return ExposureDecision(
            True,
            state,
            self._total,
            next_source,
            "exposure admitted within current budget",
        )


@dataclass(frozen=True)
class CompartmentAssignment:
    round_id: str
    task_id: str
    observer_id: str
    compartment_id: str


class CompartmentRouter:
    """Deterministically rotates assignments from a trusted private salt."""

    def __init__(self, compartments: Sequence[str]) -> None:
        cleaned = tuple(dict.fromkeys(x for x in compartments if x))
        if len(cleaned) < 2:
            raise ValueError("at least two compartments are required")
        self._compartments = cleaned

    def assign(
        self,
        *,
        round_id: str,
        task_id: str,
        observers: Sequence[str],
        private_salt: str,
    ) -> tuple[CompartmentAssignment, ...]:
        if not private_salt:
            raise ValueError("private_salt is required")
        ranked = []
        for observer in observers:
            if not observer:
                continue
            digest = hashlib.sha256(
                f"{private_salt}|{round_id}|{task_id}|{observer}".encode()
            ).hexdigest()
            ranked.append((digest, observer))
        ranked.sort()
        return tuple(
            CompartmentAssignment(
                round_id,
                task_id,
                observer,
                self._compartments[i % len(self._compartments)],
            )
            for i, (_, observer) in enumerate(ranked)
        )


@dataclass(frozen=True)
class RoleAssignment:
    round_id: str
    observer_id: str
    role: str


class RoleRotator:
    """Prevents a single observer from holding the same authority role forever."""

    def __init__(self, roles: Sequence[str]) -> None:
        self._roles = tuple(dict.fromkeys(r for r in roles if r))
        if not self._roles:
            raise ValueError("at least one role is required")

    def assign(self, round_id: str, observers: Sequence[str]) -> tuple[RoleAssignment, ...]:
        return tuple(
            RoleAssignment(
                round_id,
                observer,
                self._roles[(i + self._offset(round_id)) % len(self._roles)],
            )
            for i, observer in enumerate(observers)
            if observer
        )

    def _offset(self, round_id: str) -> int:
        raw = hashlib.sha256(round_id.encode()).hexdigest()[:8]
        return int(raw, 16) % len(self._roles)


@dataclass(frozen=True)
class IndependenceReport:
    source_count: int
    lineage_count: int
    independent: bool
    reason: str


def assess_source_independence(
    evidence: Sequence[EvidenceEnvelope],
) -> IndependenceReport:
    if not evidence:
        return IndependenceReport(0, 0, False, "no evidence")
    source_ids = {e.source_id for e in evidence if e.source_id}
    lineages = set()
    for item in evidence:
        lineages.add(
            item.parent_evidence[0]
            if item.parent_evidence
            else item.source_id
        )
    independent = len(lineages) >= 2 and len(source_ids) >= 2
    return IndependenceReport(
        len(source_ids),
        len(lineages),
        independent,
        "distinct source lineages present"
        if independent
        else "evidence shares insufficient independent lineage",
    )


@dataclass(frozen=True)
class ChallengeTrigger:
    escalate: bool
    reasons: tuple[str, ...]


class DisagreementTrigger:
    """Escalates when convergence is too easy or too unstable to trust."""

    def __init__(
        self,
        *,
        minimum_agreement: float = 0.67,
        maximum_drift: float = 0.35,
    ) -> None:
        self.minimum_agreement = minimum_agreement
        self.maximum_drift = maximum_drift

    def evaluate(
        self,
        *,
        agreement_ratio: float,
        prediction_drift: float,
        contradiction_count: int = 0,
    ) -> ChallengeTrigger:
        reasons = []
        if not 0.0 <= agreement_ratio <= 1.0:
            raise ValueError("agreement_ratio must be in [0, 1]")
        if prediction_drift < 0.0:
            raise ValueError("prediction_drift cannot be negative")
        if agreement_ratio < self.minimum_agreement:
            reasons.append("observer disagreement")
        if prediction_drift > self.maximum_drift:
            reasons.append("prediction drift")
        if contradiction_count > 0:
            reasons.append("contradiction present")
        return ChallengeTrigger(bool(reasons), tuple(reasons))


@dataclass(frozen=True)
class LockdownDecision:
    locked: bool
    reason: str


class InfluenceLockdown:
    """Freezes external authority when repeated manipulation signals accumulate."""

    def __init__(
        self,
        *,
        consecutive_high_threshold: int = 3,
        score_threshold: float = 0.60,
        trusted_witnesses: Iterable[str] = (),
    ) -> None:
        self.consecutive_high_threshold = max(1, consecutive_high_threshold)
        self.score_threshold = score_threshold
        self._trusted_witnesses = frozenset(
            x for x in trusted_witnesses if x
        )
        self._streak = 0
        self._locked = False

    @property
    def locked(self) -> bool:
        return self._locked

    def observe(self, assessment: InfluenceAssessment) -> LockdownDecision:
        if self._locked:
            return LockdownDecision(True, "lockdown already active")

        if assessment.score >= self.score_threshold:
            self._streak += 1
        else:
            self._streak = 0

        if self._streak >= self.consecutive_high_threshold:
            self._locked = True
            return LockdownDecision(
                True,
                "consecutive high-influence observations triggered lockdown",
            )

        return LockdownDecision(False, "lockdown threshold not reached")

    def reset_by_independent_witness(self, witness_id: str) -> LockdownDecision:
        if witness_id not in self._trusted_witnesses:
            raise PermissionError(
                "only explicitly trusted witnesses may reset lockdown"
            )
        self._streak = 0
        self._locked = False
        return LockdownDecision(
            False, "lockdown reset by named independent witness"
        )


@dataclass(frozen=True)
class ContainmentSnapshot:
    state: ContainmentState
    exposure: float
    locked: bool
    challenge: ChallengeTrigger
    independence: IndependenceReport


class AntiInfluenceController:
    """Single coordination surface for observation, escalation, and lockdown."""

    def __init__(
        self,
        *,
        exposure: ExposureController | None = None,
        lockdown: InfluenceLockdown | None = None,
        trigger: DisagreementTrigger | None = None,
    ) -> None:
        self.exposure = exposure or ExposureController()
        self.lockdown = lockdown or InfluenceLockdown()
        self.trigger = trigger or DisagreementTrigger()
        self.state = ContainmentState.OPEN

    def observe(
        self,
        *,
        source_id: str,
        assessment: InfluenceAssessment,
        agreement_ratio: float = 1.0,
        prediction_drift: float = 0.0,
        contradiction_count: int = 0,
        evidence: Sequence[EvidenceEnvelope] = (),
    ) -> ContainmentSnapshot:
        decision = self.exposure.admit(source_id, assessment)
        lockdown = self.lockdown.observe(assessment)
        challenge = self.trigger.evaluate(
            agreement_ratio=agreement_ratio,
            prediction_drift=prediction_drift,
            contradiction_count=contradiction_count,
        )

        states = [decision.state]
        if challenge.escalate:
            states.append(ContainmentState.ESCALATE)
        if lockdown.locked:
            states.append(ContainmentState.LOCKDOWN)

        self.state = (
            ContainmentState.LOCKDOWN
            if ContainmentState.LOCKDOWN in states
            else ContainmentState.ESCALATE
            if ContainmentState.ESCALATE in states
            else ContainmentState.CAUTION
            if ContainmentState.CAUTION in states
            else ContainmentState.OPEN
        )

        independence = assess_source_independence(evidence)
        return ContainmentSnapshot(
            self.state,
            self.exposure.total,
            lockdown.locked,
            challenge,
            independence,
        )
