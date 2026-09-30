from evez_evidence_runtime.invention import (
    CrossMapInventionEngine, InventionState, Transformation,
)
from evez_evidence_runtime.maps import MapKind, MapSpec, UniversalMapRegistry


def registry():
    return UniversalMapRegistry((
        MapSpec("repo", MapKind.REPOSITORY, "repo", "o", "s", "d", "r", "v"),
        MapSpec("workflow", MapKind.WORKFLOW, "workflow", "o", "s", "d", "r", "v"),
        MapSpec("agent", MapKind.AGENT, "agent", "o", "s", "d", "r", "v"),
    ))


def test_cross_map_routing_is_not_execution():
    engine = CrossMapInventionEngine(registry())
    engine.register_transformation(
        Transformation("t1", "reversible transition", "repo", "REVERSIBLE_TRANSITION")
    )
    result = engine.compatibility("t1", "workflow")
    assert result.compatible
    assert "execution and truth remain unverified" in result.reasons[-1]


def test_synthesis_remains_proposed():
    engine = CrossMapInventionEngine(registry())
    for ident, source in (("t1", "repo"), ("t2", "agent")):
        engine.register_transformation(
            Transformation(ident, ident, source, "RECEIPT")
        )
    invention = engine.synthesize(
        invention_id="i1",
        transformation_ids=("t1", "t2"),
        falsifiers=("output differs",),
        evidence_requirements=("receipt",),
    )
    assert invention.state == InventionState.PROPOSED
    assert invention.source_maps == ("agent", "repo")


def test_recombination_is_deterministic_and_requires_evidence():
    engine = CrossMapInventionEngine(registry())
    engine.register_transformation(Transformation("a", "a", "repo", "A"))
    engine.register_transformation(Transformation("b", "b", "workflow", "B"))
    generated = engine.generate_recombinations(prefix="gen")
    assert len(generated) == 1
    assert generated[0].state == InventionState.PROPOSED
    assert generated[0].evidence_requirements == ("execution receipt", "observed output")


def test_archive_preserves_lineage():
    engine = CrossMapInventionEngine(registry())
    engine.register_transformation(Transformation("a", "a", "repo", "A"))
    engine.synthesize(invention_id="i", transformation_ids=("a",))
    archived = engine.archive("i", "contradicted by observation")
    assert archived.state == InventionState.ARCHIVED
    assert "contradicted by observation" in archived.assumptions
