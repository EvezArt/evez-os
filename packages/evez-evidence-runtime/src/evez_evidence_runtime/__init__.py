"""EVEZ Evidence Runtime.

An executable epistemic/adversarial harness for bounded synthetic testing.
"""

from .compiler import ClaimCompiler
from .dependencies import DependencyGraph
from .federation import WitnessFederation
from .invariants import Invariant, InvariantBattery
from .ontology import EpistemicState, Relation
from .registry import Mutation, MutationRegistry
from .runtime import EvidenceRuntime, RuntimeResult
from .self_audit import SelfAuditor
from .spine import EvidenceSpine
from .surface import FailureSurface, SurfaceMapper
from .threat import ThreatCase, ThreatEngine
from .witness import WitnessEnvelope, witness

__all__ = [
    "ClaimCompiler",
    "DependencyGraph",
    "EpistemicState",
    "EvidenceRuntime",
    "EvidenceSpine",
    "FailureSurface",
    "Invariant",
    "InvariantBattery",
    "Mutation",
    "MutationRegistry",
    "Relation",
    "RuntimeResult",
    "SelfAuditor",
    "SurfaceMapper",
    "ThreatCase",
    "ThreatEngine",
    "WitnessEnvelope",
    "WitnessFederation",
    "witness",
]

__version__ = "0.1.0"
