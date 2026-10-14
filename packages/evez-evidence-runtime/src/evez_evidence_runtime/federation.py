"""Provider-neutral federation records."""
from __future__ import annotations
from dataclasses import dataclass
from .witness import WitnessEnvelope

@dataclass(frozen=True)
class FederationRecord:
    relation: str
    source_a: str
    source_b: str
    shared_keys: tuple[str, ...]
    contradiction_possible: bool
    notes: str

class WitnessFederation:
    def compare(self, a: WitnessEnvelope, b: WitnessEnvelope) -> FederationRecord:
        shared = tuple(sorted(set(a.payload) & set(b.payload)))
        contradiction_possible = any(a.payload[k] != b.payload[k] for k in shared)
        relation = "CONTRADICTS" if contradiction_possible else "CORROBORATES"
        return FederationRecord(
            relation, a.source, b.source, shared, contradiction_possible,
            "Correlation is not independence; provenance does not equal truth.",
        )
