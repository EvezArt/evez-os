#!/usr/bin/env python3
from research.information_frontier import (
    KnowledgeItem,
    SourceCapability,
    build_frontier,
)

items = [
    KnowledgeItem(
        claim_id="c-high",
        topic="weather",
        status="UNKNOWN",
        confidence=0.1,
        impact=1.0,
        novelty=1.0,
        freshness=0.9,
        last_seen=0,
    ),
    KnowledgeItem(
        claim_id="c-low",
        topic="weather",
        status="CLAIMED",
        confidence=0.9,
        impact=0.2,
        novelty=0.1,
        freshness=0.9,
        last_seen=0,
    ),
    KnowledgeItem(
        claim_id="c-conflict",
        topic="telemetry",
        status="CLAIMED",
        confidence=0.5,
        impact=0.9,
        novelty=0.8,
        freshness=0.8,
        source_id="s-old",
        contradiction_group="g1",
        last_seen=90,
    ),
]

sources = [
    SourceCapability(
        source_id="s-fast",
        topics=("weather",),
        accessible=True,
        freshness=1.0,
        estimated_cost=1.0,
        independence_group="independent",
    ),
    SourceCapability(
        source_id="s-telemetry",
        topics=("telemetry",),
        accessible=True,
        freshness=1.0,
        estimated_cost=1.0,
        independence_group="independent",
    ),
    SourceCapability(
        source_id="s-inaccessible",
        topics=("*",),
        accessible=False,
        freshness=1.0,
        estimated_cost=0.1,
    ),
]

frontier_a = build_frontier(items, sources, now_tick=100, limit=8)
frontier_b = build_frontier(items, sources, now_tick=100, limit=8)

assert frontier_a == frontier_b
assert frontier_a["scope"]["source_set_is_complete"] is False
assert frontier_a["knowledge"]["unknown"] == 1
assert frontier_a["knowledge"]["contradiction_groups"] == ["g1"]

ops = frontier_a["next_operations"]
assert ops

# The high-uncertainty/high-impact unknown should outrank a high-confidence,
# low-impact claim under the same accessible source.
assert ops[0]["claim_id"] == "c-high"

# Contradiction must create a counterevidence operation.
assert any(
    op["claim_id"] == "c-conflict" and op["action"] == "SEEK_COUNTEREVIDENCE"
    for op in ops
)

# Inaccessible sources must never become actions.
assert all(op["source_id"] != "s-inaccessible" for op in ops)

# A source count must not manufacture certainty.
assert frontier_a["principles"][0] == "Consensus does not equal truth."
assert len(frontier_a["frontier_sha256"]) == 64

print("information frontier tests: PASS")
