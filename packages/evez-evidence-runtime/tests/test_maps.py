from evez_evidence_runtime.maps import MapKind, MapSpec, UniversalMapRegistry


def test_map_registry_rejects_unbounded_authority():
    registry = UniversalMapRegistry()
    try:
        registry.register(MapSpec("bad", MapKind.SERVICE, "x", "o", "s", "d", "r", "v", authority_scope="unbounded"))
    except ValueError:
        return
    raise AssertionError("unbounded authority must be rejected")


def test_registry_routes_every_surface_through_same_contract():
    registry = UniversalMapRegistry((
        MapSpec("repo", MapKind.REPOSITORY, "github:repo", "git-observer", "spine", "decision", "bounded", "ci"),
        MapSpec("agent", MapKind.AGENT, "openclaw:agent", "agent-observer", "spine", "decision", "sandbox", status="VERIFIED"),
        MapSpec("data", MapKind.DATA, "supabase:project", "data-observer", "spine", "reconcile", "integrity", status="EVIDENCE_PENDING"),
    ))
    assert {s.map_id for s in registry.unresolved()} == {"data", "repo"}
    assert registry.routing_contract("agent")["authority_scope"] == "none-by-default"


def test_kind_filter_is_deterministic():
    registry = UniversalMapRegistry((
        MapSpec("a", MapKind.REPOSITORY, "a", "o", "s", "d", "r", "v"),
        MapSpec("b", MapKind.REPOSITORY, "b", "o", "s", "d", "r", "v"),
        MapSpec("c", MapKind.SERVICE, "c", "o", "s", "d", "r", "v"),
    ))
    assert [s.map_id for s in registry.by_kind(MapKind.REPOSITORY)] == ["a", "b"]
