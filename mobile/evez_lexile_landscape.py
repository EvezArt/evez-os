#!/usr/bin/env python3
"""Lexile landscape amplifier for observable EVEZ language."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

VERSION = "evez-lexile-landscape/v1"
PREFIXES = (
    "meta", "meta-meta", "recursive", "affective", "semantic",
    "memetic", "metamemetic", "metalinguistic",
    "metametalinguistic", "permaloot",
)
SUFFIXES = (
    "loop", "field", "landscape", "recursion", "refractor",
    "collision", "war", "humor", "loot",
)
EMOTIONS = ("tension", "anticipation", "release", "absurdity", "recognition", "wonder", "grief", "laughter")

def canonical(v: Any) -> bytes:
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()

def sha256(v: Any) -> str:
    return hashlib.sha256(canonical(v)).hexdigest()

def tokens(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower())))

def amplify(text: str, rounds: int = 3, max_nodes: int = 96) -> dict[str, Any]:
    seeds = tokens(text)
    nodes: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(term: str, roots: list[str], transform: str, layer: int, affect: str) -> None:
        term = re.sub(r"\s+", " ", term.strip())
        if not term or term in seen or len(nodes) >= max_nodes:
            return
        seen.add(term)
        payload = {
            "term": term,
            "roots": sorted(set(roots)),
            "transform": transform,
            "layer": layer,
            "affect": affect,
            "status": "PROPOSED",
        }
        nodes.append({**payload, "node_id": sha256(payload)[:16]})

    current = seeds[:]
    for root in current:
        add(root, [root], "OBSERVE", 0, "neutral")

    for layer in range(1, max(1, min(rounds, 8)) + 1):
        prior = current[:]
        current = []
        for root in prior:
            for prefix in PREFIXES:
                candidate = f"{prefix}{root}"
                affect = EMOTIONS[(len(candidate) + layer) % len(EMOTIONS)]
                add(candidate, [root], f"PREFIX:{prefix}", layer, affect)
                current.append(candidate)
            for suffix in SUFFIXES:
                candidate = f"{root}-{suffix}"
                affect = EMOTIONS[(len(candidate) + layer * 3) % len(EMOTIONS)]
                add(candidate, [root], f"SUFFIX:{suffix}", layer, affect)
                current.append(candidate)
        if len(nodes) >= max_nodes:
            break

    result = {
        "version": VERSION,
        "mode": "OBSERVABLE_LEXILE_AMPLIFICATION",
        "source_text_sha256": sha256(text),
        "seed_terms": seeds,
        "nodes": nodes,
        "edges": [
            {"from": root, "to": node["term"], "transform": node["transform"], "layer": node["layer"]}
            for node in nodes
            for root in node["roots"]
        ],
        "emotions": sorted(set(node["affect"] for node in nodes)),
        "invariants": [
            "PROPOSED != VERIFIED",
            "LANGUAGE != MIND_ACCESS",
            "EMOTION != PROOF",
            "MEME != EVIDENCE",
            "NOVEL_TERM != NEW_FACT",
        ],
    }
    result["lexile_landscape_sha256"] = sha256(result)
    return result

def main() -> int:
    parser = argparse.ArgumentParser(description="Amplify explicit lexical input.")
    parser.add_argument("text", help="Text or @FILE")
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--max-nodes", type=int, default=96)
    parser.add_argument("--output")
    args = parser.parse_args()
    text = Path(args.text[1:]).read_text(encoding="utf-8") if args.text.startswith("@") else args.text
    result = amplify(text, args.rounds, args.max_nodes)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
