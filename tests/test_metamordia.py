from rqns.audit.metamordia import (
    MetamordiaTransition,
    compare_frame_predictions,
    require_testable_transition,
)


def test_metamordia_requires_falsifier_and_test():
    transition = MetamordiaTransition(
        transition_id="M-001",
        residual_id="RES-001",
        from_frame="signal-is-noisy",
        to_frame="measurement-process-is-confounded",
        trigger="persistent unexplained residual",
        expected_distinction="confound predicts drift after calibration",
        test_ref="TEST-001",
        falsifier="calibrated replication shows no predicted drift",
    )
    digest = require_testable_transition(transition)
    assert len(digest) == 64


def test_metamordia_rejects_missing_test():
    transition = MetamordiaTransition(
        transition_id="M-002",
        residual_id="RES-002",
        from_frame="A",
        to_frame="B",
        trigger="residual",
        expected_distinction="different prediction",
        test_ref="",
        falsifier="replication contradicts prediction",
    )
    try:
        require_testable_transition(transition)
    except ValueError:
        return
    raise AssertionError("untestable frame transition was accepted")


def test_frame_transition_must_change_prediction_space():
    before = {"latency": 10, "energy": 4}
    after = {"latency": 10, "energy": 7, "drift": True}
    assert compare_frame_predictions(before, after) == ("drift", "energy")
