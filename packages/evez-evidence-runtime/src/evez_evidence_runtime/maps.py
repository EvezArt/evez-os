"""Universal ecosystem map for the EVEZ evidence/recovery/decision loop.

This registry is declarative. It routes surfaces through common observation,
evidence, decision, recovery, and verification contracts without granting
external authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MapKind(str, Enum):
    REPOSITORY = "repository"
    SERVICE = "service"
    AGENT = "agent"
    WORKFLOW = "workflow"
    DATA = "data"
    DEPLOYMENT = "deployment"
    UI = "ui"
    RESEARCH = "research"
    DOCUMENT = "document"
    INTEGRATION = "integration"


@dataclass(frozen=True)
class MapSpec:
    map_id: str
    kind: MapKind
    target: str
    observer: str
    evidence_sink: str
    decision_gate: str
    recovery_policy: str
    verification: str
    authority_scope: str = "none-by-default"
    status: str = "UNKNOWN"


class UniversalMapRegistry:
    """Canonical routing registry, not a health or deployment assertion."""

    def __init__(self, specs: tuple[MapSpec, ...] = ()) -> None:
        self._specs = {s.map_id: s for s in specs}

    def register(self, spec: MapSpec) -> None:
        if not spec.map_id.strip() or not spec.target.strip():
            raise ValueError("map_id and target required")
        if spec.authority_scope == "unbounded":
            raise ValueError("unbounded authority is not an admissible map scope")
        self._specs[spec.map_id] = spec

    def get(self, map_id: str) -> MapSpec:
        return self._specs[map_id]

    def all(self) -> tuple[MapSpec, ...]:
        return tuple(self._specs[k] for k in sorted(self._specs))

    def by_kind(self, kind: MapKind) -> tuple[MapSpec, ...]:
        return tuple(s for s in self.all() if s.kind == kind)

    def unresolved(self) -> tuple[MapSpec, ...]:
        return tuple(s for s in self.all() if s.status in {"UNKNOWN", "EVIDENCE_PENDING"})

    def routing_contract(self, map_id: str) -> dict[str, str]:
        s = self.get(map_id)
        return {
            "map_id": s.map_id, "kind": s.kind.value, "target": s.target,
            "observer": s.observer, "evidence_sink": s.evidence_sink,
            "decision_gate": s.decision_gate, "recovery_policy": s.recovery_policy,
            "verification": s.verification, "authority_scope": s.authority_scope,
            "status": s.status,
        }
