from evez_evidence_runtime.decision import NextAction, OperationalPlanner
from evez_evidence_runtime.epistemics import ClaimLineage, Falsifier
from evez_evidence_runtime.ontology import EpistemicState
from evez_evidence_runtime.optimizer import CandidateTest
from evez_evidence_runtime.recovery import FailureClass, RecoveryCatalog


def test_contradiction_quarantines_before_recovery():
    lineage = ClaimLineage("c1", "contradictory claim", contradictions=["e1 != e2"])
    decision = OperationalPlanner().decide(
        lineage=lineage,
        failure_class=FailureClass.TRANSIENT,
        recoveries=RecoveryCatalog.for_failure(FailureClass.TRANSIENT),
    )
    assert decision.action == NextAction.QUARANTINE
    assert decision.selected_id is None
    assert decision.epistemic_state == EpistemicState.CONTRADICTED


def test_authorization_never_self_authorizes():
    lineage = ClaimLineage("c2", "authorization claim", state=EpistemicState.SUPPORTED)
    decision = OperationalPlanner().decide(
        lineage=lineage,
        failure_class=FailureClass.AUTHORIZATION,
        recoveries=RecoveryCatalog.for_failure(FailureClass.AUTHORIZATION),
    )
    assert decision.action == NextAction.QUARANTINE


def test_unknown_selects_discriminating_test():
    lineage = ClaimLineage("c3", "unknown claim", state=EpistemicState.UNKNOWN)
    test = CandidateTest(
        "probe",
        "discriminating probe",
        information_gain=3,
        contradiction_resolution=2,
        reproducibility=1,
        cost=1,
        risk=0,
        discriminates=True,
        observable=True,
        safe=True,
        affects_claim=True,
    )
    decision = OperationalPlanner().decide(lineage=lineage, tests=[test])
    assert decision.action == NextAction.TEST
    assert decision.selected_id == "probe"


def test_verified_claim_has_no_automatic_action():
    lineage = ClaimLineage("c4", "verified claim", state=EpistemicState.VERIFIED)
    decision = OperationalPlanner().decide(lineage=lineage)
    assert decision.action == NextAction.NO_ACTION


def test_authorization_may_escalate_only_with_explicit_human_gate():
    lineage = ClaimLineage("c5", "authorization claim", state=EpistemicState.SUPPORTED)
    decision = OperationalPlanner().decide(
        lineage=lineage,
        failure_class=FailureClass.AUTHORIZATION,
        allow_human=True,
    )
    assert decision.action == NextAction.HUMAN_REVIEW
