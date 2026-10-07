#!/usr/bin/env python3
"""Deterministic intent optimization without inventing hidden user intent.

The optimizer ranks explicit candidate interpretations or plans. It never treats
an unstated interpretation as established fact. Ambiguous ties remain unresolved.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from typing import Any, Iterable

from research.lexile_semantics import complexity_proxy
from research.precision_contract import compile_from_intent


ACTION_WORDS = {
    "build", "create", "implement", "fix", "test", "verify", "audit",
    "inspect", "measure", "map", "classify", "compile", "deploy", "merge",
    "publish", "send", "purchase", "fund", "research", "compare", "rank",
}

URGENCY_WORDS = {"now", "today", "immediately", "urgent", "critical", "asap"}

EVIDENCE_WORDS = {
    "evidence", "source", "test", "verified", "verify", "receipt",
    "measurement", "data", "proof", "citation", "log",
}

RISK_WORDS = {
    "delete", "deploy", "merge", "publish", "send", "purchase", "fund",
    "secret", "credential", "irreversible", "production",
}


@dataclass(frozen=True)
class IntentVector:
    clarity: float
    specificity: float
    actionability: float
    evidence_density: float
    urgency: float
    reversibility: float
    semantic_complexity: float
    ambiguity: float
    risk: float
    information_gap: float


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 6)


def _term_hits(text: str, terms: set[str]) -> int:
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", text.casefold())
    return sum(token in terms for token in tokens)


def vectorize(intent: str, *, evidence: Iterable[str] = ()) -> IntentVector:
    text = " ".join(intent.split()).strip()
    if not text:
        raise ValueError("intent cannot be empty")

    precision = compile_from_intent(text)
    vague_count = len(precision["vague_terms"])
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", text)
    word_count = max(1, len(words))
    complexity = complexity_proxy(text)["proxy_units"] / 2000.0

    actionability = _bounded(_term_hits(text, ACTION_WORDS) / 2.0)
    urgency = _bounded(_term_hits(text, URGENCY_WORDS) / 2.0)
    evidence_text = " ".join(evidence)
    evidence_hits = _term_hits(text + " " + evidence_text, EVIDENCE_WORDS)
    evidence_density = _bounded(evidence_hits / max(2.0, word_count / 5.0))

    risk_hits = _term_hits(text, RISK_WORDS)
    risk = _bounded(
        0.12 * risk_hits
        + 0.22 * (1.0 if precision["status"] == "REQUIRES_SPECIFICATION" else 0.0)
    )

    ambiguity = _bounded(
        vague_count / 4.0
        + (0.25 if word_count < 3 else 0.0)
        + max(0.0, complexity - 0.85) * 0.25
    )
    specificity = _bounded(
        0.45
        + 0.22 * actionability
        + 0.18 * evidence_density
        + 0.15 * (1.0 - ambiguity)
    )
    clarity = _bounded(1.0 - ambiguity)
    reversibility = _bounded(1.0 - risk)
    information_gap = _bounded(
        0.55 * ambiguity
        + 0.25 * (1.0 - evidence_density)
        + 0.20 * (1.0 - actionability)
    )

    return IntentVector(
        clarity=clarity,
        specificity=specificity,
        actionability=actionability,
        evidence_density=evidence_density,
        urgency=urgency,
        reversibility=reversibility,
        semantic_complexity=_bounded(complexity),
        ambiguity=ambiguity,
        risk=risk,
        information_gap=information_gap,
    )


def score_vector(vector: IntentVector) -> float:
    score = (
        0.26 * vector.clarity
        + 0.20 * vector.specificity
        + 0.16 * vector.actionability
        + 0.10 * vector.evidence_density
        + 0.07 * vector.urgency
        + 0.08 * vector.reversibility
        + 0.08 * vector.information_gap
        - 0.12 * vector.risk
        - 0.07 * vector.semantic_complexity
    )
    return round(_bounded(score), 9)


def optimize_intent(
    candidates: Iterable[str],
    *,
    evidence: dict[str, Iterable[str]] | None = None,
    tie_margin: float = 0.05,
) -> dict[str, Any]:
    rows = [candidate.strip() for candidate in candidates if candidate and candidate.strip()]
    if not rows:
        return {
            "schema": "evez-intent-optimizer-v1",
            "status": "NO_CANDIDATES",
            "candidates": [],
        }

    evidence = evidence or {}
    scored: list[dict[str, Any]] = []
    for candidate in sorted(set(rows)):
        vector = vectorize(candidate, evidence=evidence.get(candidate, ()))
        precision = compile_from_intent(candidate)
        scored.append(
            {
                "intent": candidate,
                "vector": asdict(vector),
                "score": score_vector(vector),
                "precision_status": precision["status"],
                "vague_terms": precision["vague_terms"],
            }
        )

    scored.sort(key=lambda row: (-row["score"], row["intent"]))
    best = scored[0]
    second = scored[1] if len(scored) > 1 else None
    margin = round(best["score"] - second["score"], 9) if second else 1.0

    if best["precision_status"] == "REQUIRES_SPECIFICATION":
        status = "REQUIRES_SPECIFICATION"
    elif second is not None and margin < tie_margin:
        status = "AMBIGUOUS_TIE"
    elif best["vector"]["evidence_density"] < 0.15:
        status = "EVIDENCE_GAP"
    else:
        status = "OPTIMIZED_CANDIDATE"

    result = {
        "schema": "evez-intent-optimizer-v1",
        "status": status,
        "best": best,
        "runner_up": second,
        "margin": margin,
        "candidate_count": len(scored),
        "candidates": scored,
        "selection_rule": {
            "type": "weighted-bounded-score",
            "tie_margin": tie_margin,
            "unknown_over_invention": True,
        },
    }
    result["optimization_sha256"] = digest(result)
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", nargs="+")
    args = parser.parse_args()
    print(json.dumps(optimize_intent(args.candidate), indent=2, sort_keys=True))
