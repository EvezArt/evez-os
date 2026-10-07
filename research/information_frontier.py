#!/usr/bin/env python3
"""Deterministic information frontier for learning without total-world ingestion.

The frontier never assumes that the available source set is the whole Internet.
It makes coverage explicit, preserves UNKNOWN and contradiction states, and
chooses the next information-producing operation by expected information gain
per unit cost.

It is a planner, not a truth oracle.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any, Iterable


EPISTEMIC_STATES = (
    "UNKNOWN",
    "PROPOSED",
    "CLAIMED",
    "OBSERVED",
    "MEASURED",
    "REPLICATED",
    "EXPLAINED",
    "VERIFIED",
    "REJECTED",
)


@dataclass(frozen=True)
class KnowledgeItem:
    claim_id: str
    topic: str
    status: str
    confidence: float
    impact: float
    novelty: float
    freshness: float
    source_id: str | None = None
    source_accessible: bool = True
    contradiction_group: str | None = None
    last_seen: int = 0

    def validate(self) -> None:
        if self.status not in EPISTEMIC_STATES:
            raise ValueError(f"invalid epistemic status: {self.status}")
        for field_name in (
            "confidence",
            "impact",
            "novelty",
            "freshness",
        ):
            value = float(getattr(self, field_name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be within [0, 1]")
        if self.last_seen < 0:
            raise ValueError("last_seen must be non-negative")


@dataclass(frozen=True)
class SourceCapability:
    source_id: str
    topics: tuple[str, ...]
    accessible: bool
    freshness: float
    estimated_cost: float = 1.0
    independence_group: str | None = None

    def validate(self) -> None:
        if self.estimated_cost <= 0:
            raise ValueError("estimated_cost must be positive")
        if not 0.0 <= self.freshness <= 1.0:
            raise ValueError("source freshness must be within [0, 1]")


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _topic_match(source: SourceCapability, topic: str) -> bool:
    return topic in source.topics or "*" in source.topics


def choose_operations(
    items: Iterable[KnowledgeItem],
    sources: Iterable[SourceCapability],
    *,
    now_tick: int = 0,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """Select the highest-value next information operations.

    The score is deliberately explicit and bounded:
      priority = expected_information_gain / estimated_cost

    EIG is increased by uncertainty, impact, novelty, source freshness and
    disagreement. Accessibility is a hard requirement.
    """
    validated_items = list(items)
    validated_sources = list(sources)

    for item in validated_items:
        item.validate()
    for source in validated_sources:
        source.validate()

    operations: list[dict[str, Any]] = []

    for item in validated_items:
        uncertainty = 1.0 - item.confidence
        staleness = _clamp((now_tick - item.last_seen) / 100.0) if item.last_seen else 1.0
        contradiction = 1.0 if item.contradiction_group else 0.0

        if item.status == "UNKNOWN":
            action = "DISCOVER"
        elif contradiction:
            action = "SEEK_COUNTEREVIDENCE"
        elif staleness >= 0.75:
            action = "REFRESH"
        elif item.status in {"PROPOSED", "CLAIMED", "OBSERVED"}:
            action = "VERIFY"
        else:
            action = "REPLICATE"

        matching_sources = [
            source
            for source in validated_sources
            if source.accessible and _topic_match(source, item.topic)
        ]

        if not matching_sources:
            continue

        for source in matching_sources:
            independence_bonus = (
                0.15 if source.independence_group and source.independence_group != item.source_id else 0.0
            )
            freshness_gain = (source.freshness + item.freshness) / 2.0
            expected_gain = _clamp(
                uncertainty
                * (0.25 + 0.75 * item.impact)
                * (0.25 + 0.75 * item.novelty)
                * (0.25 + 0.75 * freshness_gain)
                * (1.0 + contradiction * 0.75)
                * (1.0 + independence_bonus)
            )
            priority = expected_gain / source.estimated_cost

            operations.append(
                {
                    "action": action,
                    "claim_id": item.claim_id,
                    "topic": item.topic,
                    "source_id": source.source_id,
                    "reason": (
                        "uncertainty+impact+novelty"
                        if action == "DISCOVER"
                        else action.lower()
                    ),
                    "expected_information_gain": round(expected_gain, 6),
                    "estimated_cost": round(source.estimated_cost, 6),
                    "priority": round(priority, 6),
                }
            )

    operations.sort(
        key=lambda row: (
            -row["priority"],
            row["claim_id"],
            row["source_id"],
            row["action"],
        )
    )
    return operations[: max(0, limit)]


def build_frontier(
    items: Iterable[KnowledgeItem],
    sources: Iterable[SourceCapability],
    *,
    now_tick: int = 0,
    limit: int = 8,
) -> dict[str, Any]:
    items_list = list(items)
    sources_list = list(sources)

    for item in items_list:
        item.validate()
    for source in sources_list:
        source.validate()

    accessible_sources = [s for s in sources_list if s.accessible]
    topics_known = sorted({item.topic for item in items_list})
    contradiction_groups = sorted(
        {
            item.contradiction_group
            for item in items_list
            if item.contradiction_group
        }
    )

    operations = choose_operations(
        items_list,
        sources_list,
        now_tick=now_tick,
        limit=limit,
    )

    frontier = {
        "schema": "evez-information-frontier-v1",
        "scope": {
            "source_set_is_complete": False,
            "source_set_statement": "Only explicitly registered sources are in scope.",
            "accessible_sources": len(accessible_sources),
            "registered_sources": len(sources_list),
            "known_topics": topics_known,
        },
        "knowledge": {
            "items": len(items_list),
            "unknown": sum(1 for item in items_list if item.status == "UNKNOWN"),
            "contradiction_groups": contradiction_groups,
            "contradiction_count": sum(
                1 for item in items_list if item.contradiction_group
            ),
        },
        "next_operations": operations,
        "principles": [
            "Consensus does not equal truth.",
            "Missing sources produce UNKNOWN, not negative evidence.",
            "Contradictions increase information priority.",
            "Total-world ingestion is not required for bounded learning.",
            "Every promoted conclusion requires evidence appropriate to its epistemic state.",
        ],
        "frontier_sha256": None,
    }
    frontier["frontier_sha256"] = digest(frontier)
    return frontier


def load_packet(path: str) -> tuple[list[KnowledgeItem], list[SourceCapability], int, int]:
    with open(path, "r", encoding="utf-8") as handle:
        packet = json.load(handle)

    items = [KnowledgeItem(**row) for row in packet.get("items", [])]
    sources = [
        SourceCapability(
            source_id=row["source_id"],
            topics=tuple(row.get("topics", [])),
            accessible=bool(row.get("accessible", False)),
            freshness=float(row.get("freshness", 0.0)),
            estimated_cost=float(row.get("estimated_cost", 1.0)),
            independence_group=row.get("independence_group"),
        )
        for row in packet.get("sources", [])
    ]
    return (
        items,
        sources,
        int(packet.get("now_tick", 0)),
        int(packet.get("limit", 8)),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet")
    parser.add_argument("--output")
    args = parser.parse_args()

    items, sources, now_tick, limit = load_packet(args.packet)
    result = build_frontier(items, sources, now_tick=now_tick, limit=limit)
    encoded = json.dumps(result, indent=2, sort_keys=True)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(encoded + "\n")

    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
