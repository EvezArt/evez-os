from research.cognitive_continuity import (
    CognitiveNode,
    detect_absences,
    node_digest,
    tombstone,
)

a = CognitiveNode("a", "2026-10-07T18:00:00Z", "OBSERVED", {"x": 1})
b = CognitiveNode("b", "2026-10-07T18:01:00Z", "OBSERVED", {"x": 2}, parents=("missing",))
c = CognitiveNode("c", "2026-10-07T18:02:00Z", "OBSERVED", {"x": 3}, parents=("a",))

assert len(node_digest(a)) == 64
absences = detect_absences([a, b, c])
kinds = {row.kind for row in absences}
assert "TEMPORAL_ORPHAN" in kinds
assert "LINEAGE_BREAK" in kinds

t = tombstone("a", timestamp="2026-10-07T18:03:00Z", reason="superseded")
assert t.kind == "TOMBSTONED"
assert t.subject_id == "a"

print("cognitive continuity tests: PASS")
