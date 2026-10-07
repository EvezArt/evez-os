#!/usr/bin/env python3
"""Lexile-style semantic complexity mapper.

This produces an internal complexity proxy. It is NOT a certified Lexile
measure and does not use MetaMetrics proprietary scoring.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from typing import Any

STOPWORDS = {
    "a","an","the","and","or","but","if","then","for","to","of","in","on","at",
    "by","with","from","is","are","was","were","be","been","being","this","that",
    "it","its","as","into","through","than","also","we","you","they","he","she",
    "i","my","your","our","their","all","any","some","do","does","did",
}

ABSTRACTION_MARKERS = {
    "ontology","epistemology","inference","semantics","phenomenon","taxonomy",
    "classifier","recognizer","indicator","vindicator","concept","theory",
    "framework","optimization","architecture","licensing","phenomenology",
    "causality","temporality","complexity","probability","truth","authority",
}

ROLE_TERMS = {
    "label": "LABEL",
    "classifier": "CLASSIFIER",
    "indicator": "INDICATOR",
    "recognizer": "RECOGNIZER",
    "vindicator": "VINDICATOR",
    "taxonomist": "TAXONOMIST",
    "inferenciology": "INFERENCE_DISCIPLINE",
    "ambidextrologer": "OPERATIVE_AGENT",
}

COINED_TERMS = {
    "lexilic ambidextrologers",
    "interoopticological inferenciology",
    "truth taxonimists",
    "indelumvealoquivolution",
    "materiumadulae",
}


@dataclass(frozen=True)
class SemanticAtom:
    surface: str
    normalized: str
    kind: str
    token_count: int
    syllable_estimate: int
    abstraction_density: float
    information_proxy_bits: float
    role: str | None
    coined: bool
    confidence: float


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", text.lower())


def syllables(word: str) -> int:
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    groups = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e") and groups > 1:
        groups -= 1
    return max(1, groups)


def complexity_proxy(text: str) -> dict[str, float]:
    words = tokenize(text)
    if not words:
        return {
            "word_count": 0,
            "sentence_count": 0,
            "avg_word_length": 0.0,
            "avg_syllables": 0.0,
            "content_ratio": 0.0,
            "abstraction_density": 0.0,
            "proxy_units": 0.0,
        }

    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    content = [word for word in words if word not in STOPWORDS]
    avg_word_length = sum(map(len, words)) / len(words)
    avg_syllables = sum(syllables(word) for word in words) / len(words)
    abstraction = sum(word in ABSTRACTION_MARKERS for word in words) / len(words)
    content_ratio = len(content) / len(words)
    sentence_length = len(words) / sentences

    proxy = min(
        2000.0,
        max(
            0.0,
            170
            + sentence_length * 18
            + avg_syllables * 210
            + max(0.0, avg_word_length - 4.0) * 55
            + content_ratio * 220
            + abstraction * 700,
        ),
    )
    return {
        "word_count": len(words),
        "sentence_count": sentences,
        "avg_word_length": round(avg_word_length, 3),
        "avg_syllables": round(avg_syllables, 3),
        "content_ratio": round(content_ratio, 3),
        "abstraction_density": round(abstraction, 3),
        "proxy_units": round(proxy, 3),
    }


def classify(surface: str) -> tuple[str, str | None, bool]:
    normalized = " ".join(surface.lower().split())
    if normalized in COINED_TERMS:
        return "COINED_TERM", None, True
    if normalized in ROLE_TERMS:
        role = ROLE_TERMS[normalized]
        return role, role, False
    if len(tokenize(surface)) > 1:
        return "PHRASE", None, False
    if normalized in ABSTRACTION_MARKERS:
        return "CONCEPT", None, False
    return "WORD", None, False


def map_atom(surface: str) -> SemanticAtom:
    normalized = " ".join(surface.lower().split())
    tokens = tokenize(surface)
    if not tokens:
        raise ValueError("semantic atom cannot be empty")
    kind, role, coined = classify(surface)
    abstraction = sum(
        token in ABSTRACTION_MARKERS for token in tokens
    ) / max(1, len(tokens))
    syllable_total = sum(syllables(token) for token in tokens)
    information = sum(
        math.log2(max(1, len(token)) + 1) for token in tokens
    )
    confidence = 0.95 if coined else (0.90 if kind != "WORD" else 0.75)
    return SemanticAtom(
        surface=surface,
        normalized=normalized,
        kind=kind,
        token_count=len(tokens),
        syllable_estimate=syllable_total,
        abstraction_density=round(abstraction, 3),
        information_proxy_bits=round(information, 3),
        role=role,
        coined=coined,
        confidence=confidence,
    )


def map_text(text: str) -> dict[str, Any]:
    tokens = tokenize(text)
    normalized_text = " ".join(tokens)
    candidates: set[str] = set(tokens)

    for term in COINED_TERMS:
        if term in normalized_text:
            candidates.add(term)

    for term in ROLE_TERMS:
        if re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", normalized_text):
            candidates.add(term)

    for size in (2, 3, 4):
        for index in range(max(0, len(tokens) - size + 1)):
            candidates.add(" ".join(tokens[index:index + size]))

    atoms = [
        map_atom(candidate)
        for candidate in sorted(candidates, key=lambda value: (len(tokenize(value)), value))
    ]

    result = {
        "schema": "evez-lexile-semantic-v1",
        "measure_type": "INTERNAL_PROXY_NOT_CERTIFIED_LEXILE",
        "complexity": complexity_proxy(text),
        "atoms": [asdict(atom) for atom in atoms],
        "coined_terms_present": sorted(
            {atom.normalized for atom in atoms if atom.coined}
        ),
    }
    result["mapping_sha256"] = digest(result)
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    args = parser.parse_args()
    print(json.dumps(map_text(args.text), indent=2, sort_keys=True))
