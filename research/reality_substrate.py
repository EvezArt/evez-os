# SPDX-License-Identifier: MIT
#!/usr/bin/env python3
"""Persistent causal reality substrate for EVEZ."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable

EPISTEMIC_STATES = (
    "UNKNOWN", "PROPOSED", "CLAIMED", "OBSERVED", "MEASURED",
    "REPLICATED", "EXPLAINED", "VERIFIED", "REJECTED",
)
EVENT_KINDS = (
    "OBSERVATION", "STATE_TRANSITION", "HYPOTHESIS", "ACTION",
    "CONSEQUENCE", "MEMORY", "CULTURAL_TRANSMISSION", "SIMULATION",
    "RENDER_REQUEST", "VERIFICATION",
)
REPRESENTATIONS = ("TEXT", "IMAGE", "VIDEO", "AUDIO", "THREE_D", "UI", "SIMULATION", "DATA")
WORLD_STATES = ("PROPOSED", "ACTIVE", "BRANCHED", "ARCHIVED")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


@dataclass(frozen=True)
class WorldEntity:
    entity_id: str
    entity_type: str
    state: str
    attributes: dict[str, Any]
    provenance: tuple[str, ...] = ()
    epistemic_state: str = "UNKNOWN"

    def validate(self) -> None:
        if not self.entity_id or not self.entity_type:
            raise ValueError("entity identity is required")
        if self.state not in WORLD_STATES:
            raise ValueError("invalid world state")
        if self.epistemic_state not in EPISTEMIC_STATES:
            raise ValueError("invalid epistemic state")


@dataclass(frozen=True)
class CausalEvent:
    event_id: str
    timestamp: str
    kind: str
    actor_id: str
    causes: tuple[str, ...]
    effects: tuple[str, ...]
    payload: dict[str, Any]
    evidence: tuple[str, ...] = ()
    epistemic_state: str = "PROPOSED"
    reversible: bool = True

    def validate(self) -> None:
        if not self.event_id or not self.timestamp or not self.actor_id:
            raise ValueError("event identity is incomplete")
        if self.kind not in EVENT_KINDS:
            raise ValueError("invalid event kind")
        if self.epistemic_state not in EPISTEMIC_STATES:
            raise ValueError("invalid epistemic state")
        if not self.reversible and self.epistemic_state != "VERIFIED":
            raise ValueError("irreversible event must be VERIFIED before promotion")


@dataclass(frozen=True)
class WorldSnapshot:
    snapshot_id: str
    timestamp: str
    parent_snapshot: str | None
    entities: tuple[WorldEntity, ...]
    events: tuple[CausalEvent, ...]
    branch: str = "main"

    def validate(self) -> None:
        if not self.snapshot_id or not self.timestamp:
            raise ValueError("snapshot identity is required")
        for entity in self.entities:
            entity.validate()
        for event in self.events:
            event.validate()


@dataclass(frozen=True)
class ProjectionSpec:
    projection_id: str
    representation: str
    observer_id: str
    snapshot_id: str
    parameters: dict[str, Any]

    def validate(self) -> None:
        if self.representation not in REPRESENTATIONS:
            raise ValueError("unsupported representation")
        if not self.projection_id or not self.observer_id or not self.snapshot_id:
            raise ValueError("projection identity is incomplete")


@dataclass(frozen=True)
class ArtifactManifest:
    artifact_id: str
    representation: str
    snapshot_id: str
    projection_sha256: str
    source_event_ids: tuple[str, ...]
    epistemic_state: str
    reproducible: bool


@dataclass(frozen=True)
class CounterfactualBranch:
    branch_id: str
    parent_snapshot_id: str
    assumption_event: CausalEvent
    label: str = "SIMULATED"

    def validate(self) -> None:
        if self.label not in {"SIMULATED", "COUNTERFACTUAL", "PROJECTED"}:
            raise ValueError("invalid branch label")
        self.assumption_event.validate()


@dataclass(frozen=True)
class CulturalUnit:
    unit_id: str
    parent_ids: tuple[str, ...]
    carrier: str
    payload: dict[str, Any]
    mutation_index: int
    transmission_count: int = 0

    def validate(self) -> None:
        if not self.unit_id or not self.carrier:
            raise ValueError("cultural unit identity is incomplete")
        if self.mutation_index < 0 or self.transmission_count < 0:
            raise ValueError("cultural counters cannot be negative")


@dataclass(frozen=True)
class SelfMetric:
    metric_id: str
    operation_id: str
    predicted: float
    observed: float
    resource_cost: float
    timestamp: str

    @property
    def absolute_error(self) -> float:
        return round(abs(self.predicted - self.observed), 9)

    def validate(self) -> None:
        if self.predicted < 0 or self.observed < 0 or self.resource_cost < 0:
            raise ValueError("self metrics cannot be negative")


@dataclass(frozen=True)
class DirectorCandidate:
    operation_id: str
    expected_information_gain: float
    expected_value: float
    risk: float
    resource_cost: float
    reversible: bool = True

    def validate(self) -> None:
        if self.expected_information_gain < 0 or self.expected_value < 0:
            raise ValueError("candidate value cannot be negative")
        if not 0 <= self.risk <= 1:
            raise ValueError("candidate risk must be in [0,1]")
        if self.resource_cost <= 0:
            raise ValueError("candidate resource cost must be positive")


class AppendOnlyLedger:
    def __init__(self, rows: Iterable[dict[str, Any]] = ()) -> None:
        self.rows = [dict(row) for row in rows]
        self.verify()

    @property
    def head(self) -> str:
        return self.rows[-1]["hash"] if self.rows else "GENESIS"

    def append(self, payload: dict[str, Any]) -> dict[str, Any]:
        core = {"index": len(self.rows), "parent_hash": self.head, "payload": payload}
        row = {**core, "hash": digest(core)}
        self.rows.append(row)
        return dict(row)

    def verify(self) -> None:
        previous = "GENESIS"
        for index, row in enumerate(self.rows):
            if row.get("index") != index:
                raise ValueError("ledger index discontinuity")
            if row.get("parent_hash") != previous:
                raise ValueError("ledger parent mismatch")
            core = {"index": row["index"], "parent_hash": row["parent_hash"], "payload": row["payload"]}
            if row.get("hash") != digest(core):
                raise ValueError("ledger hash mismatch")
            previous = row["hash"]

    def replay(self) -> list[dict[str, Any]]:
        self.verify()
        return [dict(row["payload"]) for row in self.rows]


def apply_event(snapshot: WorldSnapshot, event: CausalEvent) -> WorldSnapshot:
    """Create the next deterministic snapshot from one validated event.

    The function does not infer unprovided physics or causality. It records the
    event and promotes only entities explicitly named in the event effects.
    """
    snapshot.validate()
    event.validate()
    if event.event_id in {row.event_id for row in snapshot.events}:
        raise ValueError("event already exists in snapshot")

    by_id = {entity.entity_id: entity for entity in snapshot.entities}
    for entity_id in event.effects:
        if entity_id not in by_id:
            continue
        entity = by_id[entity_id]
        by_id[entity_id] = WorldEntity(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            state=entity.state,
            attributes=dict(entity.attributes),
            provenance=tuple(dict.fromkeys((*entity.provenance, event.event_id))),
            epistemic_state=entity.epistemic_state,
        )

    next_payload = {
        "parent": snapshot.snapshot_id,
        "event": event.event_id,
        "entities": sorted(by_id),
    }
    next_id = f"snap:{digest(next_payload)[:24]}"
    return WorldSnapshot(
        snapshot_id=next_id,
        timestamp=event.timestamp,
        parent_snapshot=snapshot.snapshot_id,
        entities=tuple(sorted(by_id.values(), key=lambda item: item.entity_id)),
        events=tuple((*snapshot.events, event)),
        branch=snapshot.branch,
    )

def snapshot_digest(snapshot: WorldSnapshot) -> str:
    snapshot.validate()
    return digest(asdict(snapshot))


def projection_digest(spec: ProjectionSpec) -> str:
    spec.validate()
    return digest(asdict(spec))


def compile_projection(snapshot: WorldSnapshot, spec: ProjectionSpec) -> ArtifactManifest:
    snapshot.validate()
    spec.validate()
    if spec.snapshot_id != snapshot.snapshot_id:
        raise ValueError("projection must target the supplied snapshot")
    projection_hash = projection_digest(spec)
    source_events = tuple(event.event_id for event in snapshot.events)
    artifact_id = f"{spec.representation.lower()}:{snapshot.snapshot_id}:{projection_hash[:16]}"
    return ArtifactManifest(
        artifact_id=artifact_id,
        representation=spec.representation,
        snapshot_id=snapshot.snapshot_id,
        projection_sha256=projection_hash,
        source_event_ids=source_events,
        epistemic_state="SIMULATED" if spec.representation == "SIMULATION" else "PROPOSED",
        reproducible=True,
    )


def branch_counterfactual(snapshot: WorldSnapshot, assumption_event: CausalEvent, branch_id: str) -> CounterfactualBranch:
    snapshot.validate()
    assumption_event.validate()
    if assumption_event.kind != "HYPOTHESIS":
        raise ValueError("counterfactual assumption must be a HYPOTHESIS event")
    return CounterfactualBranch(branch_id=branch_id, parent_snapshot_id=snapshot.snapshot_id, assumption_event=assumption_event)


def transmit_unit(unit: CulturalUnit, carrier: str, mutation: dict[str, Any] | None = None) -> CulturalUnit:
    unit.validate()
    payload = dict(unit.payload)
    payload.update(mutation or {})
    child_id = digest({
        "parents": [unit.unit_id],
        "carrier": carrier,
        "payload": payload,
        "mutation_index": unit.mutation_index + 1,
    })[:24]
    return CulturalUnit(
        unit_id=f"cult:{child_id}",
        parent_ids=(unit.unit_id,),
        carrier=carrier,
        payload=payload,
        mutation_index=unit.mutation_index + 1,
        transmission_count=unit.transmission_count + 1,
    )


def evaluate_self(metric: SelfMetric) -> dict[str, Any]:
    metric.validate()
    efficiency = round(
        (1.0 / max(metric.resource_cost, 1e-9)) / (1.0 + metric.absolute_error),
        9,
    )
    return {
        "schema": "evez-self-evaluation-v1",
        "metric": asdict(metric),
        "absolute_error": metric.absolute_error,
        "efficiency": efficiency,
        "improved": metric.absolute_error == 0.0,
    }


def choose_next_operation(candidates: Iterable[DirectorCandidate]) -> dict[str, Any]:
    rows = list(candidates)
    if not rows:
        return {"schema": "evez-director-v1", "status": "NO_CANDIDATES", "selected": None}
    for row in rows:
        row.validate()

    def score(row: DirectorCandidate) -> float:
        benefit = row.expected_information_gain + row.expected_value
        return round(benefit / (1.0 + row.risk) / row.resource_cost, 9)

    ranked = sorted(rows, key=lambda row: (-score(row), row.operation_id))
    selected = ranked[0]
    return {
        "schema": "evez-director-v1",
        "status": "SELECTED",
        "selection_rule": "expected_value_plus_information_gain_over_cost_and_risk",
        "selected": {**asdict(selected), "score": score(selected)},
        "candidates": [{**asdict(row), "score": score(row)} for row in ranked],
        "success_criterion_locked": True,
        "self_authorization": False,
    }
