from src.recursive.anti_influence import (
    EpistemicState,
    EvidenceEnvelope,
    InfluenceAssessment,
)
from src.recursive.anti_influence_control import (
    AntiInfluenceController,
    CompartmentRouter,
    ContainmentState,
    DisagreementTrigger,
    ExposureController,
    ExposureBudget,
    InfluenceLockdown,
    RoleRotator,
    assess_source_independence,
)


def _evidence(evidence_id: str, source_id: str):
    return EvidenceEnvelope(
        evidence_id,
        source_id,
        f"observer-{evidence_id}",
        "compartment",
        "observation",
        "channel",
        InfluenceAssessment(0.1, "LOW", ()),
    )


def test_exposure_controller_escalates_per_source_before_global_lockdown():
    controller = ExposureController(
        ExposureBudget(total_limit=2.0, source_limit=0.5)
    )
    assessment = InfluenceAssessment(0.4, "MEDIUM", ("urgency",))

    first = controller.admit("source-a", assessment)
    assert first.admitted

    second = controller.admit("source-a", assessment)
    assert not second.admitted
    assert second.state is ContainmentState.ESCALATE


def test_exposure_controller_locks_global_budget():
    controller = ExposureController(
        ExposureBudget(total_limit=0.5, source_limit=1.0)
    )
    decision = controller.admit(
        "source-a",
        InfluenceAssessment(0.7, "HIGH", ("secrecy",)),
    )
    assert not decision.admitted
    assert decision.state is ContainmentState.LOCKDOWN


def test_compartment_router_changes_assignment_with_round():
    router = CompartmentRouter(["c0", "c1", "c2"])
    a = router.assign(
        round_id="r1",
        task_id="task",
        observers=["A", "B", "C"],
        private_salt="secret",
    )
    b = router.assign(
        round_id="r2",
        task_id="task",
        observers=["A", "B", "C"],
        private_salt="secret",
    )
    assert a != b


def test_role_rotator_distributes_roles():
    rotator = RoleRotator(["SCOUT", "CHALLENGER", "WITNESS"])
    result = rotator.assign("r1", ["A", "B", "C"])
    assert {item.role for item in result} == {
        "SCOUT",
        "CHALLENGER",
        "WITNESS",
    }


def test_source_independence_requires_multiple_lineages():
    report = assess_source_independence(
        [_evidence("e1", "s1"), _evidence("e2", "s2")]
    )
    assert report.independent
    assert report.lineage_count == 2


def test_source_independence_rejects_single_lineage():
    report = assess_source_independence(
        [_evidence("e1", "s1"), _evidence("e2", "s1")]
    )
    assert not report.independent


def test_disagreement_trigger_escalates_on_drift_and_contradiction():
    trigger = DisagreementTrigger(
        minimum_agreement=0.67,
        maximum_drift=0.35,
    )
    result = trigger.evaluate(
        agreement_ratio=0.9,
        prediction_drift=0.7,
        contradiction_count=1,
    )
    assert result.escalate
    assert "prediction drift" in result.reasons
    assert "contradiction present" in result.reasons


def test_lockdown_requires_trusted_witness_to_reset():
    lock = InfluenceLockdown(
        consecutive_high_threshold=2,
        trusted_witnesses={"WITNESS"},
    )
    high = InfluenceAssessment(0.8, "HIGH", ("authority",))
    assert not lock.observe(high).locked
    assert lock.observe(high).locked

    try:
        lock.reset_by_independent_witness("UNTRUSTED")
    except PermissionError:
        pass
    else:
        raise AssertionError("untrusted witness reset lockdown")

    result = lock.reset_by_independent_witness("WITNESS")
    assert not result.locked


def test_controller_escalates_and_records_independence():
    controller = AntiInfluenceController(
        exposure=ExposureController(
            ExposureBudget(total_limit=3.0, source_limit=1.0)
        ),
        lockdown=InfluenceLockdown(
            consecutive_high_threshold=3,
            trusted_witnesses={"WITNESS"},
        ),
    )
    evidence = [_evidence("e1", "s1"), _evidence("e2", "s2")]

    result = controller.observe(
        source_id="s1",
        assessment=InfluenceAssessment(0.4, "MEDIUM", ("urgency",)),
        agreement_ratio=0.5,
        prediction_drift=0.1,
        evidence=evidence,
    )
    assert result.state is ContainmentState.ESCALATE
    assert result.challenge.escalate
    assert result.independence.independent


def test_enum_state_is_epistemic_not_influence():
    assert EpistemicState.UNKNOWN.value == "UNKNOWN"
