#!/usr/bin/env python3
"""Deterministic token-dimensional lexical analysis; Python standard library only."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOKEN_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?|[^\w\s]", re.UNICODE)
DIMENSIONS = (
    "orthographic", "phonological", "morphological", "etymological",
    "semantic", "pragmatic", "temporal", "evidence",
)
STATUSES = {"ATTESTED", "USER_SUPPLIED", "PROPOSED", "INFERRED", "UNKNOWN", "REJECTED"}
EDGE_TYPES = {
    "translation_candidate", "same_concept_candidate", "sound_association",
    "cognate_candidate", "contrast", "derivation_candidate", "semantic_neighbor",
}


def canonical_json(value: Any) -> str:
    """Stable JSON serialization for repeatable fingerprints (not a JCS implementation)."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def normalize_token(surface: str) -> str:
    return unicodedata.normalize("NFKC", surface).casefold()


def tokenize(text: str) -> list[dict[str, Any]]:
    tokens = []
    for index, match in enumerate(TOKEN_RE.finditer(text)):
        surface = match.group(0)
        tokens.append({
            "index": index,
            "surface": surface,
            "normalized": normalize_token(surface),
            "span": [match.start(), match.end()],
            "kind": "word" if any(ch.isalnum() for ch in surface) else "punctuation",
        })
    return tokens


def empty_dimensions(token: dict[str, Any]) -> dict[str, Any]:
    return {
        "orthographic": {
            "surface": token["surface"],
            "normalized": token["normalized"],
            "span": token["span"],
            "unicode_script": sorted({
                unicodedata.name(ch, "UNKNOWN").split(" ", 1)[0]
                for ch in token["surface"] if ch.isalpha()
            }),
            "status": "ATTESTED",
        },
        "phonological": {"ipa": None, "syllables": None, "notes": None, "status": "UNKNOWN"},
        "morphological": {"segments": [], "root": None, "affixes": [], "status": "UNKNOWN"},
        "etymological": {"language": None, "origin": None, "cognates": [], "source": None, "status": "UNKNOWN"},
        "semantic": {"glosses": [], "concept_ids": [], "status": "UNKNOWN"},
        "pragmatic": {"context": None, "register": None, "intended_use": None, "status": "UNKNOWN"},
        "temporal": {"first_attested": None, "period": None, "change_history": [], "status": "UNKNOWN"},
        "evidence": {"status": "UNKNOWN", "sources": [], "method": None, "confidence": None},
    }


def apply_lexicon(record: dict[str, Any], entry: dict[str, Any]) -> None:
    """Apply explicit data without upgrading its epistemic status."""
    for dimension in DIMENSIONS:
        supplied = entry.get(dimension)
        if isinstance(supplied, dict):
            record["dimensions"][dimension].update(supplied)
    # Enforce explicit statuses and evidence requirements.
    for dimension in DIMENSIONS:
        data = record["dimensions"][dimension]
        status = data.get("status", "UNKNOWN")
        if status not in STATUSES:
            raise ValueError(f"Invalid status {status!r} in {dimension}")
        if status == "ATTESTED" and dimension != "orthographic":
            if not (data.get("source") or record["dimensions"]["evidence"].get("sources")):
                raise ValueError(f"ATTESTED {dimension} requires a source reference")
    record["dimensions"]["evidence"]["status"] = entry.get(
        "evidence", {}
    ).get("status", record["dimensions"]["evidence"].get("status", "UNKNOWN"))


def domain_vector(dimensions: dict[str, Any]) -> dict[str, int]:
    vector = {}
    for name in DIMENSIONS:
        data = dimensions[name]
        meaningful = any(
            value not in (None, [], {}, "")
            for key, value in data.items()
            if key != "status"
        )
        vector[name] = int(meaningful)
    return vector


def analyze(text: str, lexicon: dict[str, Any] | None = None) -> dict[str, Any]:
    lexicon = lexicon or {}
    tokens = tokenize(text)
    records = []
    for token in tokens:
        record = {
            "token_id": f"t{token['index']:04d}-{digest(token['normalized'])[:10]}",
            "surface": token["surface"],
            "normalized": token["normalized"],
            "span": token["span"],
            "kind": token["kind"],
            "dimensions": empty_dimensions(token),
        }
        entry = lexicon.get(token["normalized"])
        if entry:
            apply_lexicon(record, entry)
        record["domain_vector"] = domain_vector(record["dimensions"])
        record["domain_occupancy"] = sum(record["domain_vector"].values())
        records.append(record)

    # Preserve exact source text and offsets: this is the prototype's reversible layer.
    reconstruction = "".join(text[token["span"][0]:token["span"][1]] for token in records)
    spans_valid = all(
        text[r["span"][0]:r["span"][1]] == r["surface"] for r in records
    )
    return {
        "schema": "evez.token-dimensional-analysis.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_text": text,
        "source_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "tokens": records,
        "token_count": len(records),
        "domain_totals": {
            name: sum(r["domain_vector"][name] for r in records) for name in DIMENSIONS
        },
        "round_trip": {
            "token_spans_valid": spans_valid,
            "token_concatenation": reconstruction,
            "exact_source_preserved": True,
            "semantic_equivalence_claimed": False,
        },
        "analysis_fingerprint": digest({
            "source": text,
            "tokens": [
                {k: r[k] for k in ("surface", "normalized", "span", "domain_vector")}
                for r in records
            ],
        }),
        "epistemic_policy": {
            "sound_similarity_is_not_etymology": True,
            "unknown_is_not_zero_evidence": True,
            "generated_candidates_default_to_proposed": True,
        },
    }


def validate_lexicon(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Lexicon root must be an object keyed by normalized token")
    for token, entry in data.items():
        if normalize_token(token) != token:
            raise ValueError(f"Lexicon key must be normalized: {token!r}")
        if not isinstance(entry, dict):
            raise ValueError(f"Entry for {token!r} must be an object")
        for dimension in DIMENSIONS:
            if dimension in entry and not isinstance(entry[dimension], dict):
                raise ValueError(f"{token}.{dimension} must be an object")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    analyze_parser = sub.add_parser("analyze", help="analyze a text string")
    analyze_parser.add_argument("text")
    analyze_parser.add_argument("--lexicon", type=Path)
    analyze_parser.add_argument("--pretty", action="store_true")
    validate_parser = sub.add_parser("validate", help="validate a lexicon JSON file")
    validate_parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)

    try:
        if args.command == "validate":
            data = validate_lexicon(args.path)
            print(json.dumps({"valid": True, "entries": len(data)}, indent=2))
            return 0
        lexicon = validate_lexicon(args.lexicon) if args.lexicon else {}
        result = analyze(args.text, lexicon)
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
