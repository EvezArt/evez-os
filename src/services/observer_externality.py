#!/usr/bin/env python3
"""EVEZ-OS Observer Externality Guard.

Separates O, I, P, M, R, and O' so internally generated representations
cannot increase the evidentiary status of a claim.
"""

from __future__ import annotations
from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping, Optional

INTERNAL_SOURCES = frozenset({"model","model_output","llm","agent","system","observer_interpretation","observer_reaction","prompt","derived","synthetic"})
EXTERNAL_SOURCES = frozenset({"sensor","instrument","human_observer","government_record","public_record","api","network","filesystem","independent_reproduction","third_party"})
STAGES = ("O","I","P","M","R","O_PRIME")

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)

def content_hash(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()

@dataclass(frozen=True)
class Observation:
    id: str
    value: Any
    source: str
    source_ref: Optional[str] = None
    external: bool = False
    observed_at: Optional[float] = None
    parent_ids: tuple[str, ...] = ()

    def normalized(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def hash(self) -> str:
        return content_hash(self.normalized())

@dataclass(frozen=True)
class InteractionTrace:
    trace_id: str
    observation: Optional[Observation] = None
    interpretation: Any = None
    prompt: Any = None
    model_output: Any = None
    observer_reaction: Any = None
    subsequent_observation: Optional[Observation] = None
    lineage: tuple[str, ...] = ()

    def stage_hashes(self) -> dict[str, str]:
        return {
            "O": content_hash(asdict(self.observation)) if self.observation else "",
            "I": content_hash(self.interpretation),
            "P": content_hash(self.prompt),
            "M": content_hash(self.model_output),
            "R": content_hash(self.observer_reaction),
            "O_PRIME": content_hash(asdict(self.subsequent_observation)) if self.subsequent_observation else "",
        }

    @property
    def hash(self) -> str:
        return content_hash({"trace_id": self.trace_id, "stage_hashes": self.stage_hashes(), "lineage": list(self.lineage)})

@dataclass(frozen=True)
class ExternalityFinding:
    code: str
    severity: str
    message: str
    trace_id: str
    evidence_weight: int
    provenance: str
    details: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class PromotionDecision:
    claim_id: str
    current_status: str
    proposed_status: str
    allowed: bool
    evidence_weight: int
    reason: str
    external_observation_ids: tuple[str, ...] = ()
    self_confirmation: bool = False

def source_class(source: str, external: bool = False) -> str:
    if external or source in EXTERNAL_SOURCES:
        return "EXTERNAL"
    if source in INTERNAL_SOURCES:
        return "INTERNAL"
    return "UNKNOWN"

def evidence_weight(source: str, external: bool = False) -> int:
    return 0 if source_class(source, external) != "EXTERNAL" else 1

def audit_trace(trace: InteractionTrace) -> list[ExternalityFinding]:
    findings: list[ExternalityFinding] = []
    obs = trace.observation
    subsequent = trace.subsequent_observation

    if trace.model_output is not None and obs is not None and subsequent is not None and not subsequent.external:
        findings.append(ExternalityFinding(
            "MODEL_DERIVED_OBSERVATION","HIGH",
            "O' is not externally sourced and cannot independently corroborate O merely because M occurred before it.",
            trace.trace_id,0,"INTERNAL",{"observation_id": subsequent.id}))

    if subsequent is not None:
        parents = set(subsequent.parent_ids)
        if trace.trace_id in parents or content_hash(trace.model_output) in parents:
            findings.append(ExternalityFinding(
                "SELF_CONFIRMATION","CRITICAL",
                "Subsequent observation explicitly descends from model output or this interaction trace.",
                trace.trace_id,0,"INTERNAL",{"parent_ids": list(subsequent.parent_ids)}))

    if obs is not None and obs.source in INTERNAL_SOURCES:
        findings.append(ExternalityFinding(
            "INTERNAL_ORIGIN","HIGH","Initial observation is internally originated.",
            trace.trace_id,0,"INTERNAL",{"source": obs.source}))

    if obs is not None and subsequent is not None:
        if subsequent.external:
            findings.append(ExternalityFinding(
                "EXTERNAL_STATE_TRANSITION","INFO",
                "O' is explicitly marked external and may contribute independent evidence subject to source verification.",
                trace.trace_id,1,"EXTERNAL",{"source": subsequent.source}))
        elif subsequent.source not in INTERNAL_SOURCES:
            findings.append(ExternalityFinding(
                "UNKNOWN_PROVENANCE","MEDIUM",
                "O' has not established whether its source is external or internally derived.",
                trace.trace_id,0,"UNKNOWN",{"source": subsequent.source}))
    return findings

def decide_promotion(claim_id: str, current_status: str, proposed_status: str, observations: Iterable[Observation], *, allowed_external_sources: Iterable[str] = EXTERNAL_SOURCES) -> PromotionDecision:
    allowed = set(allowed_external_sources)
    external_ids = [obs.id for obs in observations if obs.external and (obs.source in allowed or obs.source in EXTERNAL_SOURCES)]
    if not external_ids:
        return PromotionDecision(
            claim_id,current_status,proposed_status,False,0,
            "No independent external observation is present. Internal representations cannot promote the claim.",
            (),True)
    return PromotionDecision(
        claim_id,current_status,proposed_status,True,len(external_ids),
        "At least one explicitly external observation exists. Promotion is permitted by the externality gate, not guaranteed as truth.",
        tuple(external_ids),False)

def invariant_snapshot() -> dict[str, Any]:
    return {
        "id":"EXTERNALITY",
        "version":1,
        "rule":"Internally generated representations cannot increase the evidentiary status of a claim.",
        "stages":list(STAGES),
        "equations":{
            "MODEL_OUTPUT_CANNOT_VALIDATE_ITS_OWN_PREMISES":True,
            "representation_count != evidence_count":True,
            "internal_evidence_weight":0,
        },
        "promotion_requires":["explicit_external_source","traceable_provenance","independent_state_transition"],
        "unknown_provenance_is_not_external":True,
    }
