"""Unified next-action selection across testing, recovery, and epistemic gates.

This module is a planner only. It does not execute external effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .epistemics import ClaimLineage
from .optimizer import CandidateTest, OptimizationDecision, TestSelector
from .ontology import EpistemicState
from .recovery import (
    FailureClass,
    RecoveryAlternative,
    RecoveryDecision,
    RecoveryEngine,
)


class NextAction(str, Enum):
    TEST = "TEST"
    RECOVER = "RECOVER"
    QUARANTINE = "QUARANTINE"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    EVIDENCE_PENDING = "EVIDENCE_PENDING"
    NO_ACTION = "NO_ACTION"


@dataclass(frozen=True)
class OperationalDecision:
    action: NextAction
    selected_id: str | None
    epistemic_state: EpistemicState
    reason: str
    test_decision: OptimizationDecision | None = None
    recovery_decision: RecoveryDecision | None = None


class OperationalPlanner:
    """Choose one bounded next-step class without turning uncertainty into authority."""

    def __init__(
        self,
        *,
        test_selector: TestSelector | None = None,
        recovery_engine: RecoveryEngine | None = None,
    ) -> None:
        self.test_selector = test_selector or TestSelector()
        self.recovery_engine = recovery_engine or RecoveryEngine()

    def decide(
        self,
        *,
        lineage: ClaimLineage,
        failure_class: FailureClass | None = None,
        tests: Iterable[CandidateTest] = (),
        recoveries: Iterable[RecoveryAlternative] = (),
        allow_human: bool = False,
    ) -> OperationalDecision:
        if lineage.contradictions:
            return OperationalDecision(
                NextAction.QUARANTINE,
                None,
                EpistemicState.CONTRADICTED,
                "Unresolved contradiction blocks ordinary execution.",
            )

        if failure_class is not None:
            if failure_class == FailureClass.AUTHORIZATION:
                if allow_human:
                    return OperationalDecision(
                        NextAction.HUMAN_REVIEW,
                        None,
                        lineage.state,
                        "Authorization failure requires explicit authority adjudication.",
                    )
                return OperationalDecision(
                    NextAction.QUARANTINE,
                    None,
                    lineage.state,
                    "Authorization failure cannot self-authorize its own recovery.",
                )
            recovery = self.recovery_engine.plan(
                failure_id=lineage.claim_id,
                failure_class=failure_class,
                alternatives=recoveries,
                allow_human=allow_human,
            )
            if recovery.selected is not None:
                return OperationalDecision(
                    NextAction.RECOVER,
                    recovery.selected,
                    lineage.state,
                    "A bounded recovery alternative passed hard gates.",
                    recovery_decision=recovery,
                )

        if lineage.state in {EpistemicState.UNKNOWN, EpistemicState.PROPOSED, EpistemicState.INFERRED}:
            tests_result = self.test_selector.select(tests)
            if tests_result.selected is not None:
                return OperationalDecision(
                    NextAction.TEST,
                    tests_result.selected,
                    lineage.state,
                    "Epistemic state requires discriminating evidence before promotion.",
                    test_decision=tests_result,
                )
            return OperationalDecision(
                NextAction.EVIDENCE_PENDING,
                None,
                lineage.state,
                "No admissible discriminating test remains.",
            )

        if lineage.state == EpistemicState.VERIFIED:
            return OperationalDecision(
                NextAction.NO_ACTION,
                None,
                lineage.state,
                "No recovery or evidence action is required by the planner.",
            )

        return OperationalDecision(
            NextAction.NO_ACTION,
            None,
            lineage.state,
            "No admissible next action was identified.",
        )
