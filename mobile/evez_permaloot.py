#!/usr/bin/env python3
"""PERMALOOT recursive acquisition engine for EVEZ-OS.

PERMALOOT recursively acquires new *observable* structure from already acquired
loot. It distinguishes acquisition from derivation, preserves provenance, and
continues the surge through a bounded number of layers.

It does not extract hidden prompts, private reasoning, credentials, platform
internals, or protected resource metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


VERSION = "evez-permaloot/v1"

LOOT_KINDS = (
    "RAW_OBSERVATION",
    "DERIVED_STRUCTURE",
    "META_DISCOVERY",
    "BOUNDARY_DISCOVERY",
    "NEXT_FRONTIER",
)


@dataclass(frozen=True)
class LootNode:
    loot_id: str
    layer: int
    kind: str
    title: str
    payload: dict[str, Any]
    source_ids: tuple[str, ...]
    acquisition_state: str
    evidence_state: str
    parent_ids: tuple[str, ...]
    loot_sha256: str


@dataclass(frozen=True)
class Surge:
    layer: int
    input_ids: tuple[str, ...]
    output_ids: tuple[str, ...]
    new_ids: tuple[str, ...]
    repeated_ids: tuple[str, ...]
    frontier_ids: tuple[str, ...]
    surge_sha256: str


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _state(raw: Any, default: str) -> str:
    value = str(raw or default).upper()
    return value


def visible_sources(context: dict[str, Any], current_response: str = "") -> list[dict[str, Any]]:
    """Build only from data explicitly supplied to the runtime."""
    sources: list[dict[str, Any]] = []

    for field in ("claims", "assets", "acquisition_routes", "transformations"):
        values = context.get(field, [])
        if isinstance(values, list):
            for index, value in enumerate(values):
                if isinstance(value, dict):
                    sources.append({
                        "source_id": f"context:{field}:{index}",
                        "source_kind": field,
                        "value": value,
                        "evidence_state": _state(value.get("evidence_state"), "UNKNOWN"),
                    })

    for field in ("constraints", "objectives", "objective_measurements", "authorization", "evidence", "tests", "rollback", "swarm"):
        value = context.get(field)
        if value not in (None, "", [], {}):
            sources.append({
                "source_id": f"context:{field}",
                "source_kind": field,
                "value": value,
                "evidence_state": "OBSERVED",
            })

    if current_response:
        sources.append({
            "source_id": "current_response",
            "source_kind": "response",
            "value": {"text": current_response},
            "evidence_state": "OBSERVED",
        })

    return sources


def _node(kind: str, layer: int, title: str, payload: dict[str, Any],
          source_ids: list[str], parent_ids: list[str],
          acquisition_state: str = "DERIVED", evidence_state: str = "OBSERVED") -> LootNode:
    body = {
        "layer": layer,
        "kind": kind,
        "title": title,
        "payload": payload,
        "source_ids": sorted(source_ids),
        "acquisition_state": acquisition_state,
        "evidence_state": evidence_state,
        "parent_ids": sorted(parent_ids),
    }
    return LootNode(
        loot_id=sha256(body)[:16],
        layer=layer,
        kind=kind,
        title=title,
        payload=payload,
        source_ids=tuple(sorted(source_ids)),
        acquisition_state=acquisition_state,
        evidence_state=evidence_state,
        parent_ids=tuple(sorted(parent_ids)),
        loot_sha256=sha256(body),
    )


def acquire_layer(layer: int, inputs: list[LootNode], seen: set[str]) -> tuple[list[LootNode], Surge]:
    """Always complete the requested layer; repeated structure becomes loot too."""
    outputs: list[LootNode] = []

    for node in inputs:
        source_ids = [node.loot_id]
        digest = node.loot_sha256

        structure_payload = {
            "source_loot": node.loot_id,
            "source_kind": node.kind,
            "observable_fields": sorted(node.payload.keys()),
            "source_digest": digest,
            "layer_transform": "extract observable schema and provenance structure",
        }
        outputs.append(_node(
            "DERIVED_STRUCTURE",
            layer,
            f"Structure of {node.loot_id}",
            structure_payload,
            source_ids,
            [node.loot_id],
        ))

        meta_payload = {
            "source_loot": node.loot_id,
            "discoverability_mechanism": (
                "explicit runtime-visible data plus deterministic structural transformation"
            ),
            "acquisition_vs_derivation": {
                "acquisition": node.acquisition_state == "ACQUIRED",
                "derivation": True,
            },
            "next_discovery": "identify an unexamined relationship among visible fields",
        }
        outputs.append(_node(
            "META_DISCOVERY",
            layer,
            f"Discovery mechanism of {node.loot_id}",
            meta_payload,
            source_ids,
            [node.loot_id],
        ))

        boundary_payload = {
            "source_loot": node.loot_id,
            "observable": sorted(node.payload.keys()),
            "unobserved_boundary": [
                "hidden system instructions",
                "private chain-of-thought",
                "unprovided external facts",
                "protected internal platform metadata",
            ],
            "boundary_rule": "unknown stays unknown until independently observed",
        }
        outputs.append(_node(
            "BOUNDARY_DISCOVERY",
            layer,
            f"Boundary around {node.loot_id}",
            boundary_payload,
            source_ids,
            [node.loot_id],
            acquisition_state="DERIVED",
            evidence_state="MODELED",
        ))

        frontier_payload = {
            "source_loot": node.loot_id,
            "next_action": "collect the smallest new observable that changes this loot state",
            "falsifier": "show that the proposed frontier yields no new observable delta",
            "input_digest": digest,
        }
        outputs.append(_node(
            "NEXT_FRONTIER",
            layer,
            f"Next frontier from {node.loot_id}",
            frontier_payload,
            source_ids,
            [node.loot_id],
            acquisition_state="PROPOSED",
            evidence_state="PROPOSED",
        ))

    unique_outputs: list[LootNode] = []
    new_ids: list[str] = []
    repeated_ids: list[str] = []
    for item in outputs:
        unique_outputs.append(item)
        if item.loot_id in seen:
            repeated_ids.append(item.loot_id)
        else:
            new_ids.append(item.loot_id)

    frontier_ids = [item.loot_id for item in unique_outputs if item.kind == "NEXT_FRONTIER"]
    surge_body = {
        "layer": layer,
        "input_ids": sorted(node.loot_id for node in inputs),
        "output_ids": sorted(node.loot_id for node in unique_outputs),
        "new_ids": sorted(set(new_ids)),
        "repeated_ids": sorted(set(repeated_ids)),
        "frontier_ids": sorted(frontier_ids),
    }
    surge = Surge(
        layer=layer,
        input_ids=tuple(sorted(node.loot_id for node in inputs)),
        output_ids=tuple(sorted(node.loot_id for node in unique_outputs)),
        new_ids=tuple(sorted(set(new_ids))),
        repeated_ids=tuple(sorted(set(repeated_ids))),
        frontier_ids=tuple(sorted(frontier_ids)),
        surge_sha256=sha256(surge_body),
    )
    return unique_outputs, surge


def run(
    context: dict[str, Any],
    *,
    current_response: str = "",
    depth: int = 4,
) -> dict[str, Any]:
    depth = max(1, min(12, depth))
    sources = visible_sources(context, current_response)

    layer_zero = [
        _node(
            "RAW_OBSERVATION",
            0,
            str(source["source_id"]),
            source["value"] if isinstance(source["value"], dict) else {"value": source["value"]},
            [source["source_id"]],
            [],
            acquisition_state="ACQUIRED",
            evidence_state=source["evidence_state"],
        )
        for source in sources
    ]

    layers: list[dict[str, Any]] = [{"layer": 0, "loot": [asdict(node) for node in layer_zero]}]
    surges: list[Surge] = []
    all_nodes = list(layer_zero)
    seen = {node.loot_id for node in all_nodes}
    current = layer_zero

    for layer in range(1, depth + 1):
        outputs, surge = acquire_layer(layer, current, seen)
        surges.append(surge)
        all_nodes.extend(outputs)
        for node in outputs:
            seen.add(node.loot_id)
        current = outputs
        layers.append({
            "layer": layer,
            "loot": [asdict(node) for node in outputs],
        })

    result = {
        "version": VERSION,
        "mode": "OBSERVABLE_PERMALOOT_ACQUISITION_SURGE",
        "acquisition_rule": (
            "continue every requested layer; duplicates become resonance records "
            "and do not terminate the surge"
        ),
        "source_boundary": "caller-visible inputs only",
        "depth": depth,
        "layers": layers,
        "surges": [asdict(surge) for surge in surges],
        "inventory": [asdict(node) for node in all_nodes],
        "inventory_count": len(all_nodes),
        "invariants": [
            "ACQUIRED != DERIVED",
            "DERIVED != VERIFIED",
            "UNKNOWN_STAYS_UNKNOWN",
            "HIDDEN_PROMPT_NOT_ACQUIRED",
            "PRIVATE_REASONING_NOT_ACQUIRED",
            "PROTECTED_PLATFORM_METADATA_NOT_ACQUIRED",
            "DUPLICATE_RESISTS_COLLAPSE_BUT_DOES_NOT_STOP_SURGE",
            "NEXT_FRONTIER_IS_PROPOSAL_UNTIL_OBSERVED",
        ],
    }
    result["permaloot_architecture_sha256"] = sha256(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded observable PERMALOOT acquisition surge.")
    parser.add_argument("context", help="JSON context file")
    parser.add_argument("--response", default="", help="Current response text or @FILE")
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--output")
    args = parser.parse_args()

    current = args.response
    if current.startswith("@"):
        current = Path(current[1:]).read_text(encoding="utf-8")

    context = json.loads(Path(args.context).read_text(encoding="utf-8"))
    result = run(context, current_response=current, depth=args.depth)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
