#!/usr/bin/env python3
"""Bounded resource allocation for compute, memory, latency, energy, and attention."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class ResourceBudget:
    compute: float
    memory_mb: float
    latency_ms: float
    energy: float
    network_mb: float
    attention: float
    monetary: float = 0.0

    def validate(self) -> None:
        for field in asdict(self):
            if getattr(self, field) < 0:
                raise ValueError(f"{field} cannot be negative")


@dataclass(frozen=True)
class ResourceRequest:
    operation_id: str
    expected_value: float
    expected_information_gain: float
    urgency: float
    risk: float
    resources: ResourceBudget
    reversible: bool = True
    requires_authorization: bool = False

    def validate(self) -> None:
        if not self.operation_id:
            raise ValueError("operation_id is required")
        for name in ("expected_value", "expected_information_gain", "urgency", "risk"):
            value = float(getattr(self, name))
            if value < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.risk > 1:
            raise ValueError("risk must be <= 1")
        self.resources.validate()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def score(request: ResourceRequest) -> float:
    request.validate()
    benefit = (
        request.expected_value
        + request.expected_information_gain
        + request.urgency
    )
    penalty = 1.0 + request.risk
    cost = (
        request.resources.compute
        + request.resources.memory_mb / 1024
        + request.resources.latency_ms / 1000
        + request.resources.energy
        + request.resources.network_mb / 100
        + request.resources.attention
        + request.resources.monetary
    )
    return benefit / (penalty * max(cost, 0.001))


def allocate(
    budget: ResourceBudget,
    requests: Iterable[ResourceRequest],
    *,
    authorization_available: bool = False,
) -> dict[str, Any]:
    budget.validate()
    rows = list(requests)
    for row in rows:
        row.validate()

    remaining = budget
    ranked = sorted(rows, key=lambda row: (-score(row), row.operation_id))
    selected: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []

    for row in ranked:
        if row.requires_authorization and not authorization_available:
            deferred.append({"operation_id": row.operation_id, "reason": "AUTHORIZATION_REQUIRED"})
            continue

        r = row.resources
        fits = (
            r.compute <= remaining.compute
            and r.memory_mb <= remaining.memory_mb
            and r.latency_ms <= remaining.latency_ms
            and r.energy <= remaining.energy
            and r.network_mb <= remaining.network_mb
            and r.attention <= remaining.attention
            and r.monetary <= remaining.monetary
        )
        if not fits:
            deferred.append({"operation_id": row.operation_id, "reason": "BUDGET_EXCEEDED"})
            continue

        remaining = ResourceBudget(
            compute=remaining.compute - r.compute,
            memory_mb=remaining.memory_mb - r.memory_mb,
            latency_ms=remaining.latency_ms - r.latency_ms,
            energy=remaining.energy - r.energy,
            network_mb=remaining.network_mb - r.network_mb,
            attention=remaining.attention - r.attention,
            monetary=remaining.monetary - r.monetary,
        )
        selected.append({
            "operation_id": row.operation_id,
            "score": round(score(row), 9),
            "reversible": row.reversible,
            "authorized": not row.requires_authorization or authorization_available,
        })

    result = {
        "schema": "evez-materium-v1",
        "selected": selected,
        "deferred": deferred,
        "remaining": asdict(remaining),
        "budget_exhausted": len(deferred) > 0,
        "allocation_sha256": None,
    }
    result["allocation_sha256"] = digest(result)
    return result
