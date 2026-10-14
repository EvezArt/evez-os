from rqns.audit.consequence_provenance import (
    ConsequenceLedger,
    ConsequenceOutcome,
    ConsequencePrediction,
    consequence_delta,
)


def test_outcome_depth_and_live_lineage():
    ledger = ConsequenceLedger()
    first = ConsequenceOutcome(
        outcome_id="o0",
        parent_outcome_id=None,
        observation="baseline observed",
        enabled=("test-1",),
    )
    second = ConsequenceOutcome(
        outcome_id="o1",
        parent_outcome_id="o0",
        observation="test-1 changed the search space",
        constrained=("hypothesis-0",),
        next_tests=("test-2",),
    )
    third = ConsequenceOutcome(
        outcome_id="o2",
        parent_outcome_id="o1",
        observation="test-2 produced a new distinction",
        representation_change="frame-1",
    )

    ledger.append(first)
    ledger.append(second)
    ledger.append(third)

    assert ledger.consequence_depth("o2") == 2
    assert ledger.max_live_depth() == 2
    assert len(ledger.live_outcomes()) == 3
    assert len(ledger.snapshot_hash()) == 64


def test_verified_outcome_requires_independent_observation():
    ledger = ConsequenceLedger()
    outcome = ConsequenceOutcome(
        outcome_id="o0",
        parent_outcome_id=None,
        observation="verified result",
        status="VERIFIED",
    )
    try:
        ledger.append(outcome)
    except ValueError as exc:
        assert "independent observation" in str(exc)
    else:
        raise AssertionError("verified outcome lacked independent observation guard")


def test_prediction_requires_falsifier_and_test_reference():
    prediction = ConsequencePrediction(
        source_outcome_id="o1",
        predicted_transition="new state becomes observable",
        falsifier="no state change under controlled replay",
        test_ref="replay-001",
    )
    assert len(prediction.content_hash()) == 64


def test_consequence_delta_surfaces_new_effects():
    before = ConsequenceOutcome(
        outcome_id="before",
        parent_outcome_id=None,
        observation="before",
        enabled=("a",),
    )
    after = ConsequenceOutcome(
        outcome_id="after",
        parent_outcome_id=None,
        observation="after",
        enabled=("a", "b"),
        next_tests=("test-new",),
    )
    delta = consequence_delta(before, after)
    assert delta["enabled"] == ("b",)
    assert delta["next_tests"] == ("test-new",)
