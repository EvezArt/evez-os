from evez_evidence_runtime.failure import FailureClassifier, FailureObservation, FailureSignal
from evez_evidence_runtime.recovery import FailureClass


def test_integrity_precedes_retry():
    result = FailureClassifier().classify(
        FailureObservation(signals=frozenset({FailureSignal.TIMEOUT, FailureSignal.INTEGRITY_MISMATCH}))
    )
    assert result.failure_class == FailureClass.INTEGRITY
    assert result.evidence_sufficient


def test_unknown_stays_unknown_without_structured_signal():
    result = FailureClassifier().classify(FailureObservation())
    assert result.failure_class == FailureClass.UNKNOWN
    assert not result.evidence_sufficient


def test_authorization_boundary_is_not_recovery():
    result = FailureClassifier().classify(
        FailureObservation(signals=frozenset({FailureSignal.AUTH_DENIED}))
    )
    assert result.failure_class == FailureClass.AUTHORIZATION


def test_timeout_is_transient_but_not_an_automatic_retry_permission():
    result = FailureClassifier().classify(
        FailureObservation(signals=frozenset({FailureSignal.TIMEOUT}))
    )
    assert result.failure_class == FailureClass.TRANSIENT
