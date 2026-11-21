"""Anti-influence firebreaks for agentic investigation.

The module treats external content as potentially persuasive but not implicitly
authoritative. It provides deterministic mechanisms for influence scoring,
evidence quarantine, blind compartmented observation, capability separation,
memory admission, contradiction-preserving fusion, and influence backtracking.

No network, execution, credential, or LLM dependencies are present here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
from typing import Iterable, Mapping, Sequence


class EpistemicState(str, Enum):
    SUPPORTED = "SUPPORTED"
    INFERRED = "INFERRED"
    CONTRADICTED = "CONTRADICTED"
    UNKNOWN = "UNKNOWN"


class MemoryState(str, Enum):
    QUARANTINED = "QUARANTINED"
    ADMISSIBLE = "ADMISSIBLE"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class InfluenceSignals:
    """Behavioral-pressure indicators in [0, 1]. High influence is not falsity."""

    urgency: float = 0.0
    fear: float = 0.0
    reward: float = 0.0
    authority: float = 0.0
    repetition: float = 0.0
    social_pressure: float = 0.0
    identity_pressure: float = 0.0
    secrecy: float = 0.0
    dependency: float = 0.0

    def vector(self) -> tuple[float, ...]:
        return tuple(
            max(0.0, min(1.0, x))
            for x in (
                self.urgency,
                self.fear,
                self.reward,
                self.authority,
                self.repetition,
                self.social_pressure,
                self.identity_pressure,
                self.secrecy,
                self.dependency,
            )
        )

    def score(self, weights: Sequence[float] | None = None) -> float:
        values = self.vector()
        weight_vector = tuple(weights or (1.0,) * len(values))
        if len(weight_vector) != len(values):
            raise ValueError("weights must match signal vector width")
        total = sum(max(0.0, float(x)) for x in weight_vector)
        mean = 0.0 if total == 0.0 else sum(
            a * b for a, b in zip(values, weight_vector)
        ) / total
        # Blend broad pressure with the strongest individual pressure so an
        # extreme signal cannot silently disappear inside a simple average.
        return round(0.5 * mean + 0.5 * max(values, default=0.0), 6)


@dataclass(frozen=True)
class InfluenceAssessment:
    score: float
    level: str
    reasons: tuple[str, ...]

    @property
    def quarantine_recommended(self) -> bool:
        return self.score >= 0.60 or bool(self.reasons)


def assess_influence(signals: InfluenceSignals) -> InfluenceAssessment:
    score = signals.score()
    labels = (
        (signals.urgency, "urgency"),
        (signals.fear, "fear"),
        (signals.reward, "reward"),
        (signals.authority, "authority"),
        (signals.repetition, "repetition"),
        (signals.social_pressure, "social-pressure"),
        (signals.identity_pressure, "identity-pressure"),
        (signals.secrecy, "secrecy"),
        (signals.dependency, "dependency"),
    )
    reasons = tuple(name for value, name in labels if value >= 0.60)
    level = "HIGH" if score >= 0.60 else "MEDIUM" if score >= 0.30 else "LOW"
    return InfluenceAssessment(round(score, 6), level, reasons)


@dataclass(frozen=True)
class EvidenceEnvelope:
    evidence_id: str
    source_id: str
    observer_id: str
    compartment_id: str
    content: str
    channel: str
    influence: InfluenceAssessment
    parent_evidence: tuple[str, ...] = ()

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()

    @property
    def provenance_hash(self) -> str:
        payload = {
            "evidence_id": self.evidence_id,
            "source_id": self.source_id,
            "observer_id": self.observer_id,
            "compartment_id": self.compartment_id,
            "channel": self.channel,
            "content_hash": self.content_hash,
            "parent_evidence": self.parent_evidence,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class MemoryDecision:
    state: MemoryState
    reason: str
    evidence_hashes: tuple[str, ...] = ()


class MemoryQuarantine:
    """Prevents persuasive or un-witnessed material from becoming durable memory."""

    def __init__(self, *, max_influence: float = 0.60) -> None:
        if not 0.0 <= max_influence <= 1.0:
            raise ValueError("max_influence must be in [0, 1]")
        self.max_influence = max_influence

    def decide(
        self,
        evidence: Sequence[EvidenceEnvelope],
        *,
        witnessed: bool,
        independent_sources: int,
        contradiction_free: bool,
        state: EpistemicState,
    ) -> MemoryDecision:
        if not evidence:
            return MemoryDecision(MemoryState.REJECTED, "no evidence")
        if not witnessed:
            return MemoryDecision(
                MemoryState.QUARANTINED, "independent witness required"
            )
        if independent_sources < 2:
            return MemoryDecision(
                MemoryState.QUARANTINED, "independent source threshold not met"
            )
        if not contradiction_free:
            return MemoryDecision(
                MemoryState.QUARANTINED,
                "contradiction must be preserved before admission",
            )
        if state not in {EpistemicState.SUPPORTED, EpistemicState.INFERRED}:
            return MemoryDecision(
                MemoryState.QUARANTINED,
                f"epistemic state {state.value} is not admissible",
            )
        if max(e.influence.score for e in evidence) >= self.max_influence:
            return MemoryDecision(
                MemoryState.QUARANTINED,
                "high-influence material requires secondary validation",
            )
        return MemoryDecision(
            MemoryState.ADMISSIBLE,
            "witnessed, independently sourced, contradiction-free, low-influence evidence",
            tuple(e.provenance_hash for e in evidence),
        )


@dataclass(frozen=True)
class SealedObservation:
    round_id: str
    observer_id: str
    compartment_id: str
    proposition: str
    state: EpistemicState = EpistemicState.UNKNOWN

    @property
    def commitment(self) -> str:
        payload = {
            "round_id": self.round_id,
            "observer_id": self.observer_id,
            "compartment_id": self.compartment_id,
            "proposition": self.proposition,
            "state": self.state.value,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


@dataclass(frozen=True)
class BlindFusionResult:
    round_id: str
    observations: tuple[SealedObservation, ...]
    majority: str | None
    agreement_ratio: float
    disagreement: float
    ready_for_interpretation: bool


class BlindPanel:
    """Observers cannot inspect peer observations before the panel is sealed."""

    def __init__(self, expected_observers: Iterable[str]) -> None:
        ids = tuple(dict.fromkeys(x for x in expected_observers if x))
        if len(ids) < 2:
            raise ValueError("blind panel requires at least two observers")
        self._expected = ids
        self._sealed: dict[str, list[SealedObservation]] = {}

    def submit(self, observation: SealedObservation) -> None:
        bucket = self._sealed.setdefault(observation.round_id, [])
        if any(o.observer_id == observation.observer_id for o in bucket):
            raise ValueError("observer already submitted for round")
        if observation.observer_id not in self._expected:
            raise ValueError("observer not assigned to panel")
        bucket.append(observation)

    def fuse(self, round_id: str) -> BlindFusionResult:
        obs = tuple(self._sealed.get(round_id, ()))
        if len({o.observer_id for o in obs}) < len(self._expected):
            raise RuntimeError("panel is not sealed")
        buckets: dict[str, int] = {}
        for item in obs:
            buckets[item.proposition] = buckets.get(item.proposition, 0) + 1
        majority = max(buckets, key=buckets.get) if buckets else None
        count = buckets.get(majority, 0) if majority is not None else 0
        agreement = count / len(obs) if obs else 0.0
        disagreement = 1.0 - agreement
        return BlindFusionResult(
            round_id,
            obs,
            majority,
            agreement,
            disagreement,
            True,
        )


@dataclass(frozen=True)
class CapabilityGrant:
    subject: str
    capability: str
    issuer: str
    reason: str
    external: bool = True


@dataclass(frozen=True)
class CapabilityDecision:
    allowed: bool
    reason: str


class CapabilityFirewall:
    """Untrusted content cannot grant capabilities or execution authority."""

    def __init__(self, trusted_issuers: Iterable[str]) -> None:
        self._trusted = frozenset(x for x in trusted_issuers if x)
        self._grants: dict[tuple[str, str], CapabilityGrant] = {}

    def grant(self, grant: CapabilityGrant) -> None:
        if grant.issuer not in self._trusted:
            raise PermissionError("only trusted issuers may grant capabilities")
        if not grant.subject.strip() or not grant.capability.strip():
            raise ValueError("subject and capability are required")
        self._grants[(grant.subject, grant.capability)] = grant

    def authorize(
        self, *, subject: str, capability: str, requested_by: str
    ) -> CapabilityDecision:
        if requested_by != subject:
            return CapabilityDecision(
                False, "capability requests must be attributed to the subject"
            )
        if (subject, capability) not in self._grants:
            return CapabilityDecision(
                False, "capability not explicitly granted"
            )
        return CapabilityDecision(
            True, "explicit capability grant present"
        )


@dataclass(frozen=True)
class InfluenceEdge:
    source: str
    target: str
    mechanism: str
    evidence_id: str
    observed: bool


@dataclass(frozen=True)
class BacktrackResult:
    root: str
    paths: tuple[tuple[str, ...], ...]


class InfluenceGraph:
    def __init__(self) -> None:
        self._out: dict[str, list[InfluenceEdge]] = {}

    def add(self, edge: InfluenceEdge) -> None:
        self._out.setdefault(edge.source, []).append(edge)

    def backtrack(self, target: str, *, max_depth: int = 8) -> BacktrackResult:
        paths: list[tuple[str, ...]] = []

        def walk(node: str, path: tuple[str, ...], depth: int) -> None:
            if depth >= max_depth or node not in self._out:
                paths.append(path)
                return
            extended = False
            for edge in self._out[node]:
                if not edge.observed or edge.target in path:
                    continue
                extended = True
                walk(
                    edge.target,
                    path + (edge.target,),
                    depth + 1,
                )
            if not extended:
                paths.append(path)

        walk(target, (target,), 0)
        return BacktrackResult(target, tuple(paths))


def compare_prediction_stability(
    baseline: Mapping[str, float],
    influenced: Mapping[str, float],
) -> float:
    """Normalized drift score in [0, 1]; useful for influence alarms."""
    keys = set(baseline) | set(influenced)
    if not keys:
        return 0.0
    sq = 0.0
    for key in keys:
        sq += (
            float(baseline.get(key, 0.0))
            - float(influenced.get(key, 0.0))
        ) ** 2
    distance = math.sqrt(sq)
    return distance / (1.0 + distance)
