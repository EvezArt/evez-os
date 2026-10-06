"""Provider-neutral witness envelopes for external connector observations."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .canonical import sha256_hex

@dataclass(frozen=True)
class WitnessEnvelope:
    source: str
    observation_type: str
    observed_at: str
    payload_hash: str
    payload: dict[str, Any]
    independence_group: str
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "observation_type": self.observation_type,
            "observed_at": self.observed_at,
            "payload_hash": self.payload_hash,
            "payload": self.payload,
            "independence_group": self.independence_group,
            "notes": self.notes,
        }

def witness(source: str, observation_type: str, observed_at: str, payload: dict[str, Any], *, independence_group: str, notes: str = "") -> WitnessEnvelope:
    return WitnessEnvelope(source, observation_type, observed_at, sha256_hex(payload), payload, independence_group, notes)
