"""Cross-provider observation bridge.

Provider responses are witnesses, not truth. Contradictions survive aggregation.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .federation import FederationRecord, WitnessFederation
from .witness import WitnessEnvelope, witness

@dataclass(frozen=True)
class BridgeEvent:
    sequence: int
    source: str
    observation_type: str
    witness: WitnessEnvelope

class EvidenceBridge:
    def __init__(self) -> None:
        self.events: list[BridgeEvent] = []
        self._sequence = 0

    def ingest(self, *, source: str, observation_type: str, observed_at: str, payload: dict[str, Any], independence_group: str, notes: str = "") -> WitnessEnvelope:
        self._sequence += 1
        envelope = witness(source, observation_type, observed_at, payload, independence_group=independence_group, notes=notes)
        self.events.append(BridgeEvent(self._sequence, source, observation_type, envelope))
        return envelope

    def compare(self, a: WitnessEnvelope, b: WitnessEnvelope) -> FederationRecord:
        return WitnessFederation().compare(a, b)

    def sources(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(event.source for event in self.events))

    def by_source(self, source: str) -> list[WitnessEnvelope]:
        return [event.witness for event in self.events if event.source == source]

    def export(self) -> list[dict[str, Any]]:
        return [
            {
                "sequence": e.sequence,
                "source": e.source,
                "observation_type": e.observation_type,
                "witness": e.witness.to_dict(),
            }
            for e in self.events
        ]
