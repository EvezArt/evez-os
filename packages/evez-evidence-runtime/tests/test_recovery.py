from evez_evidence_runtime.recovery import (
    FailureClass, RecoveryAlternative, RecoveryBudget, RecoveryEngine, RecoveryState
)


def alt(**kw):
    base = dict(
        action_id="retry",
        description="bounded retry",
        failure_classes=frozenset({FailureClass.TRANSIENT}),
        safe=True, authorized=True, observable=True, reversible=True,
        idempotent=True, compensatable=False, cost=1, risk=.1,
        information_gain=2, blast_radius=.1, retryable=True,
        expected_observation="dependency responds",
    )
    base.update(kw)
    return RecoveryAlternative(**base)


def test_recovery_rejects_unsafe_unauthorized_and_blind_actions():
    d = RecoveryEngine().plan(
        failure_id="f1", failure_class=FailureClass.TRANSIENT,
        alternatives=[
            alt(action_id="unsafe", safe=False),
            alt(action_id="unauthorized", authorized=False),
            alt(action_id="blind", observable=False),
        ],
    )
    assert d.selected is None
    assert d.rejected["unsafe"] == "unsafe"
    assert d.rejected["unauthorized"] == "unauthorized"
    assert d.rejected["blind"] == "no-observable"


def test_non_idempotent_retry_requires_compensation():
    d = RecoveryEngine().plan(
        failure_id="f2", failure_class=FailureClass.TRANSIENT,
        alternatives=[alt(action_id="unsafe-retry", idempotent=False, compensatable=False)],
    )
    assert d.selected is None
    assert d.rejected["unsafe-retry"] == "retry-without-idempotency-or-compensation"


def test_dominated_recovery_is_pruned():
    d = RecoveryEngine().plan(
        failure_id="f3", failure_class=FailureClass.TRANSIENT,
        alternatives=[
            alt(action_id="strong", cost=1, risk=.1, blast_radius=.1, information_gain=5),
            alt(action_id="weak", cost=2, risk=.2, blast_radius=.2, information_gain=4),
        ],
    )
    assert d.selected == "strong"
    assert d.rejected["weak"] == "dominated"


def test_budget_is_enforced():
    engine = RecoveryEngine(budget=RecoveryBudget(max_attempts=1))
    assert engine.begin_attempt()
    assert not engine.begin_attempt()


def test_integrity_failure_quarantines_to_cain():
    d = RecoveryEngine().plan(
        failure_id="f4", failure_class=FailureClass.INTEGRITY,
        alternatives=[alt(action_id="wrong-class")],
    )
    assert d.selected is None
    assert d.state == RecoveryState.CAIN


def test_unknown_is_not_success():
    assert RecoveryEngine.classify_observation(expected=True, observed=False) == RecoveryState.NEXT_ALTERNATIVE
    assert RecoveryEngine.classify_observation(expected=True, observed=True, contradictory=True) == RecoveryState.CAIN
    assert RecoveryEngine.classify_observation(expected=False, observed=True) == RecoveryState.EVIDENCE_PENDING
