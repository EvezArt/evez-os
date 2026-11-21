"""Structured failure classification without speculative text inference."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FailureSignal(str, Enum):
    TIMEOUT = "TIMEOUT"
    RATE_LIMIT = "RATE_LIMIT"
    CAPACITY = "CAPACITY"
    AUTH_DENIED = "AUTH_DENIED"
    INTEGRITY_MISMATCH = "INTEGRITY_MISMATCH"
    CONFIG_INVALID = "CONFIG_INVALID"
    DEPENDENCY_UNAVAILABLE = "DEPENDENCY_UNAVAILABLE"
    DEPLOYMENT_FAILED = "DEPLOYMENT_FAILED"
    PROVENANCE_MISSING = "PROVENANCE_MISSING"
    ADVERSARIAL_INPUT = "ADVERSARIAL_INPUT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class FailureObservation:
    signals: frozenset[FailureSignal] = frozenset()
    retry_after_seconds: float | None = None
    dependency_name: str | None = None
    evidence_ids: tuple[str, ...] = ()

    @property
    def is_observed(self) -> bool:
        return bool(self.signals and FailureSignal.UNKNOWN not in self.signals)


@dataclass(frozen=True)
class FailureClassification:
    failure_class: "FailureClass"
    evidence_sufficient: bool
    rationale: tuple[str, ...]


class FailureClassifier:
    """Map structured observations to recovery classes; never infer from prose."""

    def classify(self, observation: FailureObservation) -> FailureClassification:
        from .recovery import FailureClass

        s = observation.signals
        if not s or FailureSignal.UNKNOWN in s:
            return FailureClassification(
                FailureClass.UNKNOWN,
                False,
                ("No sufficient structured failure signal.",),
            )

        if FailureSignal.INTEGRITY_MISMATCH in s:
            return FailureClassification(
                FailureClass.INTEGRITY,
                True,
                ("Integrity mismatch has precedence over ordinary retry signals.",),
            )
        if FailureSignal.AUTH_DENIED in s:
            return FailureClassification(
                FailureClass.AUTHORIZATION,
                True,
                ("Authorization denial requires an authority decision.",),
            )
        if FailureSignal.PROVENANCE_MISSING in s:
            return FailureClassification(
                FailureClass.PROVENANCE,
                True,
                ("Missing provenance blocks epistemic promotion.",),
            )
        if FailureSignal.ADVERSARIAL_INPUT in s:
            return FailureClassification(
                FailureClass.ADVERSARIAL,
                True,
                ("Adversarial input requires isolation and witnessed handling.",),
            )
        if FailureSignal.CONFIG_INVALID in s:
            return FailureClassification(
                FailureClass.CONFIGURATION,
                True,
                ("Configuration invalidity is deterministic from the structured signal.",),
            )
        if FailureSignal.DEPLOYMENT_FAILED in s:
            return FailureClassification(
                FailureClass.DEPLOYMENT,
                True,
                ("Deployment failure is explicitly observed.",),
            )
        if FailureSignal.CAPACITY in s or FailureSignal.RATE_LIMIT in s:
            return FailureClassification(
                FailureClass.CAPACITY,
                True,
                ("Capacity or rate-limit signals constrain load.",),
            )
        if FailureSignal.DEPENDENCY_UNAVAILABLE in s:
            return FailureClassification(
                FailureClass.DEPENDENCY,
                True,
                ("Dependency availability signal is explicit.",),
            )
        if FailureSignal.TIMEOUT in s:
            return FailureClassification(
                FailureClass.TRANSIENT,
                True,
                ("Timeout alone supports transient classification, not guaranteed retry.",),
            )
        return FailureClassification(
            FailureClass.PERSISTENT,
            True,
            ("Observed structured failure lacks a more specific class.",),
        )
