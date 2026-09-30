from evez_evidence_runtime.epistemics import ClaimLineage
from evez_evidence_runtime.failure import FailureObservation, FailureSignal
from evez_evidence_runtime.maps import MapKind, MapSpec, UniversalMapRegistry
from evez_evidence_runtime.reconcile import MapReconciler


def test_reconcile_never_promotes_missing_evidence():
    registry = UniversalMapRegistry((
        MapSpec("api", MapKind.SERVICE, "evez-api", "o", "spine", "d", "r", "v"),
    ))
    lineage = ClaimLineage("api-health", "API healthy")
    result = MapReconciler(registry).reconcile(map_id="api", lineage=lineage)
    assert result.epistemic_state == "UNKNOWN"
    assert result.failure_class == "UNKNOWN"
    assert result.next_action == "EVIDENCE_PENDING"


def test_reconcile_turns_structured_dependency_failure_into_action():
    registry = UniversalMapRegistry((
        MapSpec("api", MapKind.SERVICE, "evez-api", "o", "spine", "d", "r", "v"),
    ))
    lineage = ClaimLineage("api-health", "API healthy")
    observation = FailureObservation(
        signals=frozenset({FailureSignal.DEPENDENCY_UNAVAILABLE}),
        dependency_name="api",
        evidence_ids=("obs-1",),
    )
    result = MapReconciler(registry).reconcile(
        map_id="api",
        lineage=lineage,
        observation=observation,
        observed_state="UNAVAILABLE",
        evidence_ids=("obs-1",),
    )
    assert result.failure_class == "DEPENDENCY"
    assert result.next_action == "RECOVER"
    assert result.evidence_ids == ("obs-1",)


def test_reconcile_is_deterministic():
    registry = UniversalMapRegistry((
        MapSpec("a", MapKind.SERVICE, "a", "o", "s", "d", "r", "v"),
        MapSpec("b", MapKind.SERVICE, "b", "o", "s", "d", "r", "v"),
    ))
    reconciler = MapReconciler(registry)
    inputs = [
        ("b", ClaimLineage("b", "b"), None, "UNKNOWN", ()),
        ("a", ClaimLineage("a", "a"), None, "UNKNOWN", ()),
    ]
    first = reconciler.reconcile_many(inputs)
    second = reconciler.reconcile_many(inputs)
    assert first == second
