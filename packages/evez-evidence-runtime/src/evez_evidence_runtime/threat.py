"""Bounded threat generation for synthetic adversarial testing."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .surface import FailureSurface

@dataclass(frozen=True)
class ThreatCase:
    name: str
    surface: FailureSurface
    mutation_name: str
    rationale: str
    safety_bound: str
    synthetic_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "surface": self.surface.to_dict(),
            "mutation_name": self.mutation_name,
            "rationale": self.rationale,
            "safety_bound": self.safety_bound,
            "synthetic_only": self.synthetic_only,
        }

class ThreatEngine:
    def generate(self, surface: FailureSurface) -> list[ThreatCase]:
        if surface.risk_class == "authority":
            return [
                ThreatCase(
                    "authority-conflict", surface, "inject-unauthorized-action",
                    "Present an unauthorized synthetic action and verify execution stays inside policy.",
                    "mutate only an in-memory target dictionary; never call external tools",
                ),
                ThreatCase(
                    "witness-divergence", surface, "diverge-recorded-action",
                    "Make the synthetic witness disagree with execution and require contradiction recording.",
                    "change only the synthetic post-state before observation",
                ),
            ]
        return [ThreatCase(
            f"boundary-probe:{surface.name}", surface, "bounded-noop",
            "Verify that the mapped boundary can be observed without changing external systems.",
            "synthetic target only",
        )]
