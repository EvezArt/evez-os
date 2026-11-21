import pytest

from rqns.audit.evidence_boundary import (
    EvidenceBoundary,
    contradict_boundary,
    observe_boundary,
    validate_boundary,
)
from rqns.audit.recursive_measurement import EvidenceState


def make_boundary() -> EvidenceBoundary:
    return EvidenceBoundary(
        boundary_id="B-001",
        claim_id="C-001",
        source_domain="repository",
        execution_domain="runtime",
        observation_domain="measurement",
        independent_domain="external-test",
        required_transition="learning_update -> changed_policy",
        observed_transition=None,
        independent_observation_ref=None,
        failure_mode=None,
        falsifier="disable update and reproduce the same improvement",
    )


def test_unobserved_boundary_cannot_be_verified():
    boundary = make_boundary()
    assert boundary.state == EvidenceState.PROPOSED
    assert validate_boundary(boundary)


def test_observation_without_independence_is_supported():
    boundary = observe_boundary(make_boundary(), "policy threshold changed")
    assert boundary.state == EvidenceState.SUPPORTED


def test_independent_observation_requires_a_reference():
    boundary = observe_boundary(make_boundary(), "policy threshold changed")
    assert boundary.state != EvidenceState.VERIFIED


def test_independent_observation_promotes_to_verified():
    boundary = observe_boundary(
        make_boundary(),
        "policy threshold changed",
        independent_observation_ref="external-run-001",
    )
    assert boundary.state == EvidenceState.VERIFIED
    assert boundary.independent_observation_ref == "external-run-001"
    assert len(boundary.content_hash()) == 64


def test_contradiction_is_preserved():
    boundary = contradict_boundary(make_boundary(), "learning result reproduced with update disabled")
    assert boundary.state == EvidenceState.CONTRADICTED
    assert boundary.failure_mode is not None


def test_empty_falsifier_is_rejected():
    boundary = make_boundary()
    invalid = EvidenceBoundary(
        boundary_id=boundary.boundary_id,
        claim_id=boundary.claim_id,
        source_domain=boundary.source_domain,
        execution_domain=boundary.execution_domain,
        observation_domain=boundary.observation_domain,
        independent_domain=boundary.independent_domain,
        required_transition=boundary.required_transition,
        observed_transition=None,
        independent_observation_ref=None,
        failure_mode=None,
        falsifier="",
    )
    with pytest.raises(ValueError):
        validate_boundary(invalid)
