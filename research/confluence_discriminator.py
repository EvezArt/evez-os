"""Cross-source temporal confluence discriminator.

The detector is deliberately provenance-first. A synchronized burst is not
itself a threat signal. The same geometry can be produced by one operator,
shared automation, scheduled jobs, or independent actors coordinating.

Input events require:
  ts, actor, text
Optional:
  repo, source, committer, url

The classifier never assigns motive. It classifies the evidence regime:
  INTERNAL_OPERATOR_BURST
  AUTOMATION_BURST
  CANDIDATE_COORDINATION
  UNKNOWN_INSUFFICIENT_EVIDENCE
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
import math
import random
import re
from collections import Counter, defaultdict
from typing import Any, Iterable, Sequence


STOP = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with",
    "from", "add", "update", "fix", "docs", "feat", "chore", "test",
}


@dataclass(frozen=True)
class Event:
    ts: float
    actor: str
    text: str = ""
    source: str = "unknown"
    repo: str = ""
    committer: str = ""
    url: str = ""

    @staticmethod
    def from_mapping(row: dict[str, Any]) -> "Event":
        raw = row.get("ts", row.get("timestamp"))
        if isinstance(raw, (int, float)):
            ts = float(raw)
        elif isinstance(raw, str):
            value = raw.replace("Z", "+00:00")
            ts = datetime.fromisoformat(value).timestamp()
        else:
            raise ValueError("event requires ts/timestamp")

        return Event(
            ts=ts,
            actor=str(row.get("actor", "unknown")),
            text=str(row.get("text", "")),
            source=str(row.get("source", row.get("source_type", "unknown"))),
            repo=str(row.get("repo", "")),
            committer=str(row.get("committer", "")),
            url=str(row.get("url", "")),
        )


@dataclass(frozen=True)
class ConfluenceConfig:
    window_seconds: int = 300
    min_events: int = 3
    similarity_threshold: float = 0.72
    candidate_actor_min: int = 3
    permutations: int = 250
    random_seed: int = 666
    max_events: int = 20_000


@dataclass
class ClusterResult:
    cluster_id: str
    event_count: int
    actors: int
    committers: int
    sources: int
    repos: int
    semantic_similarity: float
    temporal_surprise_z: float
    temporal_p_value: float
    independent_actor_ratio: float
    independent_source_ratio: float
    label: str
    rationale: list[str] = field(default_factory=list)


def _tokens(text: str) -> set[str]:
    clean = re.sub(r"https?://\S+", " ", text.lower())
    clean = re.sub(r"[^a-z0-9_#/-]+", " ", clean)
    return {
        token for token in clean.split()
        if len(token) > 1 and token not in STOP
    }


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _pairwise_similarity(events: Sequence[Event]) -> float:
    if len(events) < 2:
        return 0.0
    sets = [_tokens(e.text) for e in events]
    values: list[float] = []
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            values.append(_jaccard(sets[i], sets[j]))
    return sum(values) / len(values) if values else 0.0


def _bucket_counts(events: Sequence[Event], seconds: int) -> list[int]:
    buckets: Counter[int] = Counter(int(e.ts // seconds) for e in events)
    return list(buckets.values())


def _burst_stat(events: Sequence[Event], seconds: int) -> float:
    counts = _bucket_counts(events, seconds)
    if not counts:
        return 0.0
    return float(max(counts))


def _permutation_z(events: Sequence[Event], cfg: ConfluenceConfig) -> tuple[float, float]:
    """Compare the observed max bucket occupancy to shuffled timestamps."""
    if len(events) < cfg.min_events:
        return 0.0, 1.0

    observed = _burst_stat(events, cfg.window_seconds)
    times = [e.ts for e in events]
    lo, hi = min(times), max(times)
    span = max(cfg.window_seconds, hi - lo)
    rng = random.Random(cfg.random_seed)
    maxima: list[float] = []

    # Preserve the number of events while destroying temporal structure.
    for _ in range(max(1, cfg.permutations)):
        shuffled = [
            Event(ts=rng.uniform(lo, lo + span), actor=e.actor, text=e.text,
                  source=e.source, repo=e.repo, committer=e.committer, url=e.url)
            for e in events
        ]
        maxima.append(_burst_stat(shuffled, cfg.window_seconds))

    mean = sum(maxima) / len(maxima)
    variance = sum((x - mean) ** 2 for x in maxima) / max(1, len(maxima) - 1)
    sd = math.sqrt(variance)
    z = (observed - mean) / sd if sd > 1e-12 else (10.0 if observed > mean else 0.0)
    p = (1 + sum(x >= observed for x in maxima)) / (len(maxima) + 1)
    return z, p


def _ratio_distinct(values: Iterable[str]) -> float:
    vals = [v for v in values if v]
    return len(set(vals)) / max(1, len(vals))


def _make_clusters(events: Sequence[Event], cfg: ConfluenceConfig) -> list[list[Event]]:
    ordered = sorted(events, key=lambda e: e.ts)
    clusters: list[list[Event]] = []
    current: list[Event] = []

    for event in ordered:
        if not current or event.ts - current[-1].ts <= cfg.window_seconds:
            current.append(event)
        else:
            if len(current) >= cfg.min_events:
                clusters.append(current)
            current = [event]

    if len(current) >= cfg.min_events:
        clusters.append(current)
    return clusters


def classify_cluster(cluster: Sequence[Event], cfg: ConfluenceConfig, idx: int) -> ClusterResult:
    actors = {e.actor for e in cluster if e.actor}
    committers = {e.committer for e in cluster if e.committer}
    sources = {e.source for e in cluster if e.source}
    repos = {e.repo for e in cluster if e.repo}
    similarity = _pairwise_similarity(cluster)
    z, p = _permutation_z(cluster, cfg)

    actor_ratio = _ratio_distinct(e.actor for e in cluster)
    source_ratio = _ratio_distinct(e.source for e in cluster)

    rationale: list[str] = []
    label = "UNKNOWN_INSUFFICIENT_EVIDENCE"

    if len(actors) == 1 and len(sources) == 1:
        label = "INTERNAL_OPERATOR_BURST"
        rationale.append("all events share one actor and one source")
    elif len(actors) <= 2 and any("bot" in a.lower() or "dependabot" in a.lower() for a in actors):
        label = "AUTOMATION_BURST"
        rationale.append("actor set is dominated by a known automation identity")
    elif (
        len(actors) >= cfg.candidate_actor_min
        and len(sources) >= 2
        and similarity >= cfg.similarity_threshold
        and z >= 2.5
        and p <= 0.05
    ):
        label = "CANDIDATE_COORDINATION"
        rationale.extend([
            "multiple distinct actors",
            "multiple independent sources",
            "semantic reuse exceeds threshold",
            "temporal concentration exceeds shuffled null expectation",
        ])
    else:
        rationale.append("observed confluence does not satisfy independent-actor + source + null-model gates")

    return ClusterResult(
        cluster_id=f"confluence_{idx:03d}",
        event_count=len(cluster),
        actors=len(actors),
        committers=len(committers),
        sources=len(sources),
        repos=len(repos),
        semantic_similarity=round(similarity, 4),
        temporal_surprise_z=round(z, 4),
        temporal_p_value=round(p, 4),
        independent_actor_ratio=round(actor_ratio, 4),
        independent_source_ratio=round(source_ratio, 4),
        label=label,
        rationale=rationale,
    )


def analyze(events: Iterable[Event | dict[str, Any]], cfg: ConfluenceConfig | None = None) -> dict[str, Any]:
    cfg = cfg or ConfluenceConfig()
    parsed: list[Event] = []
    for item in events:
        parsed.append(item if isinstance(item, Event) else Event.from_mapping(item))
        if len(parsed) >= cfg.max_events:
            break

    clusters = _make_clusters(parsed, cfg)
    results = [classify_cluster(c, cfg, i + 1) for i, c in enumerate(clusters)]
    labels = Counter(result.label for result in results)

    return {
        "events_analyzed": len(parsed),
        "clusters_analyzed": len(results),
        "labels": dict(labels),
        "results": [result.__dict__ for result in results],
        "policy": {
            "no_attribution_from_confluence": True,
            "candidate_requires_multi_actor_multi_source": True,
            "null_model": "timestamp permutation with fixed actor/source/message marginals",
        },
    }


def stable_cluster_fingerprint(result: ClusterResult) -> str:
    material = "|".join([
        result.cluster_id,
        str(result.event_count),
        str(result.actors),
        str(result.sources),
        result.label,
    ])
    return sha256(material.encode()).hexdigest()
