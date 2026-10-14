from evez_evidence_runtime.epistemics import (
    ClaimLineage,
    Falsifier,
    epistemic_conservation_violation,
    promote,
)
from evez_evidence_runtime.ontology import EpistemicState

def test_verified_promotion_requires_observation_test_and_falsifier():
    lineage = ClaimLineage("c1", "A bounded claim.")
    lineage.source_observations.append("obs1")
    lineage.tests.append("test1")
    lineage.add_falsifier(Falsifier("f1", "observable failure", "actual_state"))
    result = promote(lineage, EpistemicState.VERIFIED, new_evidence=True)
    assert result.allowed
    assert lineage.state == EpistemicState.VERIFIED

def test_verified_promotion_without_new_evidence_is_blocked():
    lineage = ClaimLineage("c2", "Unsupported precision.")
    lineage.source_observations.append("obs1")
    lineage.tests.append("test1")
    lineage.add_falsifier(Falsifier("f1", "failure", "x"))
    result = promote(lineage, EpistemicState.VERIFIED, new_evidence=False)
    assert not result.allowed
    assert lineage.state == EpistemicState.PROPOSED

def test_epistemic_conservation_blocks_free_certainty():
    assert epistemic_conservation_violation(
        EpistemicState.UNKNOWN, EpistemicState.VERIFIED, new_evidence=False
    )
    assert not epistemic_conservation_violation(
        EpistemicState.UNKNOWN, EpistemicState.VERIFIED, new_evidence=True
    )
