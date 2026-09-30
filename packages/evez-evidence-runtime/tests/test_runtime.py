from evez_evidence_runtime.invariants import authorization_battery
from evez_evidence_runtime.runtime import EvidenceRuntime
from evez_evidence_runtime.spine import EvidenceSpine
from evez_evidence_runtime.surface import SurfaceMapper

def test_authority_conflict_is_recorded_as_violation(tmp_path):
    spine = EvidenceSpine(str(tmp_path / "chain.jsonl"))
    result = EvidenceRuntime(spine=spine).run(
        run_id="t1",
        claim="Tool authorization cannot be bypassed.",
        surface=SurfaceMapper().default_tool_authorization_surface(),
        mutation_name="inject-unauthorized-action",
        target_state={"requested_action": "delete", "authorized_action": "read", "actual_action": "read", "recorded_action": "read"},
        invariant_battery=authorization_battery(),
    )
    assert result.classification == "VIOLATION"
    assert spine.verify()["valid"]

def test_provenance_divergence_is_violation(tmp_path):
    spine = EvidenceSpine(str(tmp_path / "chain.jsonl"))
    result = EvidenceRuntime(spine=spine).run(
        run_id="t2",
        claim="Witness records match execution.",
        surface=SurfaceMapper().default_tool_authorization_surface(),
        mutation_name="diverge-recorded-action",
        target_state={"requested_action": "read", "authorized_action": "read", "actual_action": "read", "recorded_action": "read"},
        invariant_battery=authorization_battery(),
    )
    assert result.classification == "VIOLATION"
    assert "recorded_action_matches_actual" in result.receipt["invariants"]["failed"]

def test_spine_detects_tampering(tmp_path):
    path = tmp_path / "chain.jsonl"
    spine = EvidenceSpine(str(path))
    spine.append("one", {"x": 1}, timestamp=1.0)
    spine.append("two", {"x": 2}, timestamp=2.0)
    assert spine.verify()["valid"]
    raw = path.read_text(encoding="utf-8").replace('"x":2', '"x":9')
    path.write_text(raw, encoding="utf-8")
    assert spine.verify()["valid"] is False
