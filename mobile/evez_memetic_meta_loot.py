#!/usr/bin/env python3
"""Memetic meta-humor layer for EVEZ PERMALOOT.

Turns observable PERMALOOT artifacts into traceable meta-jokes. The joke is
allowed to recurse on the mechanism that generated the joke, but never needs
hidden prompts, private reasoning, or fabricated facts.

PERMANENT_LOOT means persistent recursive lineage, not infinite execution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


VERSION = "evez-memetic-meta-loot/v1"

PATTERNS = (
    ("SELF_REFERENCE", "The system discovered that it was itself part of the loot."),
    ("BOUNDARY_JOKE", "The boundary became observable, so the boundary became content."),
    ("LOOP_JOKE", "The next frontier is apparently the frontier having another frontier."),
    ("PROVENANCE_JOKE", "The receipt is now examining the receipt printer."),
    ("UNKNOWN_JOKE", "UNKNOWN survived the loot cycle and somehow became the most honest artifact."),
    ("AUTHORITY_JOKE", "The judge audited itself and immediately had to audit the audit."),
    ("REPETITION_JOKE", "The duplicate refused to be discarded and was promoted to lore."),
    ("COMPRESSION_JOKE", "The packet got smaller while its implications got larger."),
)


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def extract_signals(permaloot: dict[str, Any]) -> list[dict[str, Any]]:
    signals = []
    inventory = permaloot.get("inventory", [])
    for node in inventory:
        if not isinstance(node, dict):
            continue
        kind = str(node.get("kind", ""))
        payload = node.get("payload", {})
        signals.append({
            "loot_id": node.get("loot_id"),
            "layer": node.get("layer"),
            "kind": kind,
            "payload_keys": sorted(payload.keys()) if isinstance(payload, dict) else [],
            "parent_ids": node.get("parent_ids", []),
        })
    return signals


def generate_memes(permaloot: dict[str, Any], max_memes: int = 32) -> list[dict[str, Any]]:
    signals = extract_signals(permaloot)
    if not signals:
        return []

    memes: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(kind: str, punchline: str, sources: list[str], layer: int) -> None:
        body = {
            "kind": kind,
            "punchline": punchline,
            "source_loot_ids": sorted(x for x in sources if x),
            "layer": layer,
        }
        meme_id = sha256(body)[:16]
        if meme_id in seen:
            return
        seen.add(meme_id)
        memes.append({
            **body,
            "meme_id": meme_id,
            "status": "GENERATED_FROM_OBSERVABLE_LOOT",
            "meme_sha256": sha256(body),
        })

    for node in signals:
        lid = node["loot_id"]
        layer = int(node.get("layer") or 0)
        kind = node["kind"]
        if kind == "BOUNDARY_DISCOVERY":
            add("BOUNDARY_JOKE", "The wall was labeled UNKNOWN, then the runtime put the wall in the museum.",
                [lid], layer)
        elif kind == "NEXT_FRONTIER":
            add("LOOP_JOKE", "Congratulations: the next objective is to discover what the objective was doing here.",
                [lid], layer)
        elif kind == "META_DISCOVERY":
            add("PROVENANCE_JOKE", "We looted the loot, then looted the explanation for why the loot was loot.",
                [lid], layer)
        elif kind == "DERIVED_STRUCTURE":
            add("SELF_REFERENCE", "The artifact has become evidence about the artifact becoming an artifact.",
                [lid], layer)

    layers = sorted({int(x.get("layer") or 0) for x in signals})
    if len(layers) >= 2:
        add("SELF_REFERENCE",
            "PERMALOOT has reached the forbidden administrative discovery: its own paperwork is now loot.",
            [x["loot_id"] for x in signals if int(x.get("layer") or 0) == max(layers)],
            max(layers))

    boundary_ids = [x["loot_id"] for x in signals if x["kind"] == "BOUNDARY_DISCOVERY"]
    next_ids = [x["loot_id"] for x in signals if x["kind"] == "NEXT_FRONTIER"]
    if boundary_ids and next_ids:
        add("BOUNDARY_JOKE",
            "The system found the edge of the map, then filed the edge under 'places to loot next.'",
            boundary_ids[:4] + next_ids[:4],
            max(layers))

    return memes[:max_memes]


def run(permaloot: dict[str, Any], max_memes: int = 32) -> dict[str, Any]:
    memes = generate_memes(permaloot, max_memes=max_memes)
    result = {
        "version": VERSION,
        "mode": "PERSISTENT_MEMETIC_PERMALOOT",
        "source_architecture_sha256": permaloot.get("permaloot_architecture_sha256"),
        "memes": memes,
        "memetic_inventory_count": len(memes),
        "persistence_rule": (
            "Every meme retains source loot IDs and source architecture digest; "
            "a later PERMALOOT generation may loot the meme layer as observable input."
        ),
        "humor_rules": [
            "JOKE != FACT",
            "MEME != EVIDENCE",
            "IRONY != AUTHORITY",
            "RECURSION != INFINITY",
            "SOURCE_TRACEABILITY_PRESERVED",
        ],
    }
    result["memetic_meta_loot_sha256"] = sha256(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Loot PERMALOOT for traceable memetic meta-humor.")
    parser.add_argument("permaloot_json", help="PERMALOOT JSON output")
    parser.add_argument("--max-memes", type=int, default=32)
    parser.add_argument("--output")
    args = parser.parse_args()

    data = json.loads(Path(args.permaloot_json).read_text(encoding="utf-8"))
    result = run(data, max_memes=max(1, min(256, args.max_memes)))
    rendered = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
