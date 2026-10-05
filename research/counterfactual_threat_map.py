"""Counterfactual threat mapping.

The detector separates anomaly from coordination. An unusual burst can be produced
by one operator, CI, Dependabot, mirrors, retries, or generated commits. Coordination
requires independent actors and independent sources in addition to a statistic that
survives a counterfactual null.

No attribution, motive, identity targeting, or hidden-cause inference is performed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import random
import re
from collections import defaultdict
from typing import Any, Iterable


@dataclass(frozen=True)
class Event:
    ts: float
    actor: str
    text: str
    source: str
    url: str = ""


def _ts(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()


def normalize_text(text: str) -> str:
    text = re.sub(r"https?://\S+", " URL ", text or "")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s_/#-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _ngrams(text: str, n: int = 3) -> set[str]:
    compact = normalize_text(text).replace(" ", "_")
    if not compact:
        return set()
    return {compact[i : i + n] for i in range(max(0, len(compact) - n + 1))}


def _jaccard(a: set[str], b: set[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 1.0


def parse_events(rows: Iterable[dict[str, Any]]) -> list[Event]:
    return [
        Event(
            ts=_ts(row["ts"]),
            actor=str(row.get("actor", "UNKNOWN")),
            text=str(row.get("text", "")),
            source=str(row.get("source", row.get("domain", "UNKNOWN"))),
            url=str(row.get("url", "")),
        )
        for row in rows
    ]


def _burst_stat(events: list[Event], bucket_seconds: int) -> int:
    buckets: dict[int, set[tuple[str, str]]] = defaultdict(set)
    for e in events:
        bucket = int(e.ts // bucket_seconds)
        buckets[bucket].add((e.actor, e.source))
    return sum(
        1
        for values in buckets.values()
        if len({a for a, _ in values}) >= 2 and len({s for _, s in values}) >= 2
    )


def _shape_stat(events: list[Event], threshold: float = 0.82) -> int:
    grams = [_ngrams(e.text) for e in events]
    total = 0
    for i in range(len(events)):
        for j in range(i + 1, len(events)):
            if events[i].actor == events[j].actor:
                continue
            if _jaccard(grams[i], grams[j]) >= threshold:
                total += 1
    return total


def _permute_actors(events: list[Event], rng: random.Random) -> list[Event]:
    actors = [e.actor for e in events]
    rng.shuffle(actors)
    return [
        Event(ts=e.ts, actor=actors[i], text=e.text, source=e.source, url=e.url)
        for i, e in enumerate(events)
    ]


def _permutation_pvalue(observed: int, null: list[int]) -> float:
    if not null:
        return 1.0
    return (1 + sum(x >= observed for x in null)) / (len(null) + 1)


def analyze(
    rows: Iterable[dict[str, Any]],
    *,
    bucket_seconds: int = 600,
    permutations: int = 500,
    seed: int = 7,
    shape_threshold: float = 0.82,
) -> dict[str, Any]:
    events = parse_events(rows)
    if not events:
        return {
            "state": "UNKNOWN",
            "reason": "no events",
            "observed": {},
            "null": {},
            "guardrails": {},
        }

    actors = {e.actor for e in events}
    sources = {e.source for e in events}
    observed_burst = _burst_stat(events, bucket_seconds)
    observed_shape = _shape_stat(events, shape_threshold)

    rng = random.Random(seed)
    burst_null: list[int] = []
    shape_null: list[int] = []
    for _ in range(max(0, permutations)):
        permuted = _permute_actors(events, rng)
        burst_null.append(_burst_stat(permuted, bucket_seconds))
        shape_null.append(_shape_stat(permuted, shape_threshold))

    p_burst = _permutation_pvalue(observed_burst, burst_null)
    p_shape = _permutation_pvalue(observed_shape, shape_null)

    burst_p95 = sorted(burst_null)[max(0, int(len(burst_null) * 0.95) - 1)] if burst_null else 0
    shape_p95 = sorted(shape_null)[max(0, int(len(shape_null) * 0.95) - 1)] if shape_null else 0

    independent_axes = len(actors) >= 2 and len(sources) >= 2
    survives_null = p_burst < 0.01 and p_shape < 0.05
    coordination_supported = independent_axes and survives_null

    if coordination_supported:
        state = "SUPPORTED_COORDINATION_SIGNAL"
    elif independent_axes and (p_burst < 0.05 or p_shape < 0.05):
        state = "ANOMALY_REQUIRES_REVIEW"
    elif not independent_axes:
        state = "ANOMALY_NOT_COORDINATION_EVIDENCE"
    else:
        state = "NO_COORDINATION_SIGNAL"

    return {
        "state": state,
        "observed": {
            "events": len(events),
            "unique_actors": len(actors),
            "unique_sources": len(sources),
            "burst_stat": observed_burst,
            "shape_stat": observed_shape,
        },
        "null": {
            "permutations": permutations,
            "seed": seed,
            "burst_p95": burst_p95,
            "shape_p95": shape_p95,
            "burst_p_value": round(p_burst, 6),
            "shape_p_value": round(p_shape, 6),
        },
        "guardrails": {
            "requires_independent_actors": True,
            "requires_independent_sources": True,
            "no_motive_inference": True,
            "no_identity_attribution": True,
            "coordination_requires_null_survival": True,
        },
        "derived": {
            "independent_axes": independent_axes,
            "survives_null": survives_null,
            "coordination_supported": coordination_supported,
        },
    }
