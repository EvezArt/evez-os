"""EVEZ Evidence Runtime.

Executable epistemic/adversarial harness for bounded synthetic testing.
"""

from .compiler import ClaimCompiler
from .dependencies import DependencyGraph
from .federation import WitnessFederation
from .integration_bridge import EvidenceBridge
from .invariants import Invariant, InvariantBattery
from .ontology import EpistemicState, Relation
from .optimizer import CandidateTest, OptimizationDecision, TestSelector
from .registry import Mutation, MutationRegistry
from .runtime import EvidenceRuntime, RuntimeResult
from .self_audit import SelfAuditor
from .spine import EvidenceSpine
from .surface import FailureSurface, SurfaceMapper
from .threat import ThreatCase, ThreatEngine
from .witness import WitnessEnvelope, witness

__all__ = [
    "CandidateTest", "ClaimCompiler", "DependencyGraph", "EpistemicState",
    "EvidenceBridge", "EvidenceRuntime", "EvidenceSpine", "FailureSurface",
    "Invariant", "InvariantBattery", "Mutation", "MutationRegistry",
    "OptimizationDecision", "Relation", "RuntimeResult", "SelfAuditor",
    "SurfaceMapper", "TestSelector", "ThreatCase", "ThreatEngine",
    "WitnessEnvelope", "WitnessFederation", "witness",
]

__version__ = "0.2.0"
