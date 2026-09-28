from rqns.audit.metacognitive_allocator import (
    AllocationLedger,
    Investigation,
    RepresentationTransition,
)


def test_allocation_is_deterministic_and_not_a_truth_score():
    ledger = AllocationLedger()
    items = [
        Investigation("I2", "R2", 1.0, 0.8, 0.7, 0.9, 2.0, 0.5, 1.0, 0.9),
        Investigation("I1", "R1", 1.0, 0.8, 0.7, 0.9, 1.0, 0.5, 1.0, 0.9),
    ]
    ranked = ledger.allocate(items)
    assert ranked[0][0] == "I1"
    assert ranked[0][1] > ranked[1][1]


def test_representation_transition_leaves_a_verifiable_footprint():
    ledger = AllocationLedger()
    transition = RepresentationTransition(
        transition_id="METAMORDIA-001",
        residual_id="RES-017",
        from_frame="prediction_error",
        to_frame="measurement_process",
        trigger="persistent unexplained residual",
        expected_distinction="observer effect becomes testable",
        test_ref="TEST-017",
    )
    digest = ledger.record_transition(transition)
    assert len(digest) == 64
    assert ledger.audit_transition("METAMORDIA-001")


def test_transition_without_test_ref_is_not_auditable():
    ledger = AllocationLedger()
    transition = RepresentationTransition(
        transition_id="METAMORDIA-002",
        residual_id="RES-018",
        from_frame="A",
        to_frame="B",
        trigger="residual",
        expected_distinction="new distinction",
        test_ref="",
    )
    ledger.record_transition(transition)
    assert not ledger.audit_transition("METAMORDIA-002")
