from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Sequence
import hashlib
import json


class EpistemicState(str, Enum):
    SUPPORTED = "SUPPORTED"
    INFERRED = "INFERRED"
    CONTRADICTED = "CONTRADICTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Claim:
    claim_id: str
    proposition: str
    subject: str
    predicate: str
    object: str
    state: EpistemicState = EpistemicState.UNKNOWN


@dataclass(frozen=True)
class CounterHypothesis:
    challenge_id: str
    claim_id: str
    proposition: str
    predicted_observable: float | None
    rationale: str


@dataclass(frozen=True)
class AttackResult:
    challenge_id: str
    observable: float | None
    expected_error: float | None
    contradiction: bool
    evidence_ref: str
    note: str = ""


@dataclass(frozen=True)
class VerificationRule:
    min_supporting_attacks: int = 1
    max_contradictions: int = 0
    require_independent_evidence: bool = True


@dataclass(frozen=True)
class ClaimAssessment:
    claim: Claim
    counter_hypotheses: tuple[CounterHypothesis, ...]
    attacks: tuple[AttackResult, ...]
    state: EpistemicState
    reason: str
    evidence_hash: str = ""

    def canonical_bytes(self) -> bytes:
        payload = {
            "claim": self.claim.__dict__,
            "counter_hypotheses": [c.__dict__ for c in self.counter_hypotheses],
            "attacks": [a.__dict__ for a in self.attacks],
            "state": self.state.value,
            "reason": self.reason,
        }
        payload["claim"]["state"] = self.claim.state.value
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class AdversarialClaimCompiler:
    def __init__(self, rule: VerificationRule | None = None) -> None:
        self.rule = rule or VerificationRule()

    @staticmethod
    def propose_counter_hypotheses(
        claim: Claim,
        alternatives: Iterable[tuple[str, float | None, str]],
    ) -> tuple[CounterHypothesis, ...]:
        return tuple(
            CounterHypothesis(
                f"{claim.claim_id}:CH{i}",
                claim.claim_id,
                proposition,
                prediction,
                rationale,
            )
            for i, (proposition, prediction, rationale) in enumerate(alternatives, 1)
        )

    def assess(
        self,
        claim: Claim,
        counter_hypotheses: Sequence[CounterHypothesis],
        attacks: Sequence[AttackResult],
    ) -> ClaimAssessment:
        if not claim.proposition.strip() or not attacks:
            state = EpistemicState.UNKNOWN
            reason = "claim or adversarial evidence is missing"
        else:
            contradictions = [a for a in attacks if a.contradiction]
            independent = [a for a in attacks if a.evidence_ref.strip()]
            if contradictions:
                state = EpistemicState.CONTRADICTED
                reason = f"{len(contradictions)} attack result(s) contradict the claim"
            elif len(independent) >= self.rule.min_supporting_attacks:
                state = EpistemicState.SUPPORTED
                reason = f"{len(independent)} adversarial result(s) failed to contradict the claim"
            else:
                state = EpistemicState.INFERRED
                reason = "evidence is consistent but verification is incomplete"

        updated = Claim(
            claim.claim_id,
            claim.proposition,
            claim.subject,
            claim.predicate,
            claim.object,
            state,
        )
        return ClaimAssessment(updated, tuple(counter_hypotheses), tuple(attacks), state, reason)


def finalize_assessment(assessment: ClaimAssessment) -> ClaimAssessment:
    unsigned = ClaimAssessment(
        assessment.claim,
        assessment.counter_hypotheses,
        assessment.attacks,
        assessment.state,
        assessment.reason,
    )
    return ClaimAssessment(
        assessment.claim,
        assessment.counter_hypotheses,
        assessment.attacks,
        assessment.state,
        assessment.reason,
        unsigned.content_hash(),
    )
