from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Protocol, Sequence

from .adversarial_claim import AttackResult, Claim, CounterHypothesis


class CounterHypothesisGenerator(Protocol):
    def generate(
        self, claim: Claim, context: Mapping[str, object]
    ) -> Sequence[CounterHypothesis]:
        ...


@dataclass
class CallableChallenger:
    fn: Callable[[Claim, Mapping[str, object]], Sequence[CounterHypothesis]]

    def generate(
        self, claim: Claim, context: Mapping[str, object]
    ) -> Sequence[CounterHypothesis]:
        return tuple(self.fn(claim, context))


@dataclass(frozen=True)
class ChallengePlan:
    claim_id: str
    challenge_ids: tuple[str, ...]
    required_evidence: int = 1


def build_challenge_plan(
    claim: Claim,
    hypotheses: Sequence[CounterHypothesis],
    required_evidence: int = 1,
) -> ChallengePlan:
    return ChallengePlan(
        claim.claim_id,
        tuple(h.challenge_id for h in hypotheses),
        max(1, int(required_evidence)),
    )


def validate_attack_set(
    plan: ChallengePlan,
    attacks: Sequence[AttackResult],
) -> tuple[bool, str]:
    if not plan.challenge_ids:
        return False, "no counter-hypotheses were generated"

    known = set(plan.challenge_ids)
    seen = {a.challenge_id for a in attacks}

    if seen - known:
        return False, "attack references an unknown challenge"

    if len(known & seen) < plan.required_evidence:
        return False, "insufficient challenge coverage"

    if any(not a.evidence_ref.strip() for a in attacks):
        return False, "attack evidence reference is required"

    return True, "attack set is structurally valid"
