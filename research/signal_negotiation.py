#!/usr/bin/env python3
"""Deterministic capability negotiation for the EVEZ signal domain."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable

SIGNAL_STATES = (
    "PREPARE",
    "RENDER",
    "DELIVER",
    "ACK",
    "FALLBACK",
    "EXPIRED",
    "FAILED",
)


@dataclass(frozen=True)
class ChannelCapability:
    channel: str
    available: bool
    consent_scopes: tuple[str, ...]
    attention: float
    reliability: float
    cost: float
    max_priority: float = 1.0
    preferred_rank: int = 100

    def validate(self) -> None:
        if self.cost <= 0:
            raise ValueError("channel cost must be positive")
        for name in ("attention", "reliability", "max_priority"):
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be within [0,1]")
        if self.preferred_rank < 0:
            raise ValueError("preferred_rank must be non-negative")


@dataclass(frozen=True)
class NegotiationRequest:
    signal_id: str
    intent: str
    priority: float
    consent_scope: str
    max_channels: int = 3
    require_redundancy: bool = False
    min_reliability: float = 0.0

    def validate(self) -> None:
        if not self.signal_id:
            raise ValueError("signal_id is required")
        if self.max_channels <= 0:
            raise ValueError("max_channels must be positive")
        if not 0.0 <= self.priority <= 1.0:
            raise ValueError("priority must be within [0,1]")
        if not 0.0 <= self.min_reliability <= 1.0:
            raise ValueError("min_reliability must be within [0,1]")
        if not self.consent_scope:
            raise ValueError("consent_scope is required")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def negotiate(
    request: NegotiationRequest,
    capabilities: Iterable[ChannelCapability],
) -> dict[str, Any]:
    request.validate()
    caps = list(capabilities)
    for cap in caps:
        cap.validate()

    candidates: list[dict[str, Any]] = []
    for cap in caps:
        consented = request.consent_scope in cap.consent_scopes or "*" in cap.consent_scopes
        eligible = (
            cap.available
            and consented
            and cap.reliability >= request.min_reliability
            and request.priority <= cap.max_priority
        )
        if not eligible:
            continue

        value = (
            (0.25 + 0.75 * cap.attention)
            * (0.25 + 0.75 * cap.reliability)
            * (0.5 + 0.5 * request.priority)
        ) / cap.cost

        candidates.append({
            "channel": cap.channel,
            "score": round(value, 6),
            "attention": cap.attention,
            "reliability": cap.reliability,
            "cost": cap.cost,
            "preferred_rank": cap.preferred_rank,
        })

    candidates.sort(
        key=lambda row: (-row["score"], row["preferred_rank"], row["channel"])
    )

    target_count = 1
    if request.require_redundancy:
        target_count = min(2, request.max_channels)
    elif request.intent == "CRITICAL" or request.priority >= 0.9:
        target_count = min(2, request.max_channels)

    selected = candidates[:target_count]

    if not selected:
        status = "NO_ELIGIBLE_CHANNEL"
    elif len(selected) < target_count:
        status = "DEGRADED"
    else:
        status = "READY"

    plan = {
        "schema": "evez-indelumvealoquivolution-v1",
        "signal_id": request.signal_id,
        "intent": request.intent,
        "status": status,
        "requested_redundancy": request.require_redundancy,
        "selected_channels": selected,
        "candidate_count": len(candidates),
        "reachable_channels": len(
            [
                cap for cap in caps
                if cap.available
                and (request.consent_scope in cap.consent_scopes or "*" in cap.consent_scopes)
            ]
        ),
        "fallback_order": [row["channel"] for row in candidates],
        "constraints": {
            "consent_scope": request.consent_scope,
            "min_reliability": request.min_reliability,
            "max_channels": request.max_channels,
        },
        "plan_sha256": None,
    }
    plan["plan_sha256"] = digest(plan)
    return plan
