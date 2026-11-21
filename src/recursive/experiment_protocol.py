"""Canonical experiment records for recursive active measurement.

Records are append-only at the protocol level. A caller can serialize each
record into the existing EventSpine/chain ledger without coupling the engine
to a particular storage backend.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any, Mapping, Sequence, Tuple


Vector = Tuple[float, ...]


@dataclass(frozen=True)
class ExperimentRecord:
    run_id: str
    tick: int
    state_before: Vector
    action_label: str
    action_value: float
    observable_channel: str
    observable_value: float
    observed_state: Vector
    counterfactual_state: Vector
    measurement_influence: float
    prediction_error: float
    selected_model: str
    parent_hash: str = "genesis"

    def canonical_bytes(self) -> bytes:
        return json.dumps(
            asdict(self),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    def as_event(self) -> Mapping[str, Any]:
        return {
            "domain": "recursive-phenomenon",
            "event_type": "measurement-back-action",
            "payload": asdict(self),
            "content_hash": self.content_hash(),
        }


def chain(records: Sequence[ExperimentRecord]) -> list[ExperimentRecord]:
    """Return records with deterministic parent hashes."""
    out: list[ExperimentRecord] = []
    parent = "genesis"
    for record in records:
        updated = ExperimentRecord(
            **{**asdict(record), "parent_hash": parent}
        )
        out.append(updated)
        parent = updated.content_hash()
    return out
