from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Mapping, Sequence

from .adversarial_claim import (
    AdversarialClaimCompiler,
    AttackResult,
    Claim,
    ClaimAssessment,
    CounterHypothesis,
    EpistemicState,
    finalize_assessment,
)
from .challenger import ChallengePlan, build_challenge_plan, validate_attack_set
from .experiment_protocol import ExperimentRecord


@dataclass(frozen=True)
class WitnessFinding:
    ok: bool
    code: str
    detail: str


def _distance(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("state width mismatch")
    return sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def verify_record(record: ExperimentRecord) -> tuple[WitnessFinding, ...]:
    findings: list[WitnessFinding] = []
    if not record.run_id.strip():
        findings.append(WitnessFinding(False, "MISSING_RUN_ID", "run_id is empty"))
    if len(record.observed_state) != len(record.counterfactual_state):
        findings.append(WitnessFinding(False, "STATE_WIDTH_MISMATCH", "state widths differ"))
    else:
        expected = _distance(record.observed_state, record.counterfactual_state)
        if abs(expected - record.measurement_influence) > 1e-9:
            findings.append(WitnessFinding(False, "INFLUENCE_MISMATCH", "recorded influence differs from recomputed influence"))
    if not findings:
        findings.append(WitnessFinding(True, "RECORD_VALID", "independent checks passed"))
    return tuple(findings)


def verify_chain(records: Sequence[ExperimentRecord]) -> tuple[WitnessFinding, ...]:
    findings: list[WitnessFinding] = []
    parent = "genesis"
    for index, record in enumerate(records):
        if record.parent_hash != parent:
            findings.append(WitnessFinding(False, "BROKEN_PARENT_CHAIN", f"index={index}"))
        findings.extend(verify_record(record))
        parent = record.content_hash()
    if not findings:
        findings.append(WitnessFinding(True, "CHAIN_VALID", f"{len(records)} records verified"))
    return tuple(findings)


@dataclass(frozen=True)
class AdversarialWitnessReport:
    assessment: ClaimAssessment
    plan: ChallengePlan
    structurally_valid: bool
    structural_reason: str

    @property
    def state(self) -> EpistemicState:
        return self.assessment.state

    @property
    def machine_verifiable(self) -> bool:
        return self.structurally_valid and len(self.assessment.evidence_hash) == 64


class AdversarialWitness:
    def __init__(
        self,
        challenger,
        compiler: AdversarialClaimCompiler | None = None,
    ) -> None:
        self.challenger = challenger
        self.compiler = compiler or AdversarialClaimCompiler()

    def prepare(
        self,
        claim: Claim,
        context: Mapping[str, object] | None = None,
    ) -> tuple[CounterHypothesis, ...]:
        return tuple(self.challenger.generate(claim, context or {}))

    def assess(
        self,
        claim: Claim,
        hypotheses: Sequence[CounterHypothesis],
        attacks: Sequence[AttackResult],
    ) -> AdversarialWitnessReport:
        plan = build_challenge_plan(
            claim, hypotheses, required_evidence=len(hypotheses)
        )
        valid, reason = validate_attack_set(plan, attacks)
        if valid:
            assessment = finalize_assessment(
                self.compiler.assess(claim, hypotheses, attacks)
            )
        else:
            assessment = finalize_assessment(
                ClaimAssessment(
                    claim,
                    tuple(hypotheses),
                    tuple(attacks),
                    EpistemicState.UNKNOWN,
                    f"witness rejected attack set: {reason}",
                )
            )
        return AdversarialWitnessReport(assessment, plan, valid, reason)
