"""EVEZ Evidence Runtime.

Executable epistemic/adversarial harness for bounded synthetic testing.
"""

from .compiler import ClaimCompiler
from .dependencies import DependencyGraph
from .epistemics import ClaimLineage, Falsifier, PromotionResult, promote
from .federation import WitnessFederation
from .integration_bridge import EvidenceBridge
from .invariants import Invariant, InvariantBattery
from .ontology import EpistemicState, Relation
from .optimizer import CandidateTest, OptimizationDecision, TestSelector
from .registry import Mutation, MutationRegistry
from .recovery import FailureClass, RecoveryAlternative, RecoveryBudget, RecoveryDecision, RecoveryEngine, RecoveryReceipt, RecoveryState
from .runtime import EvidenceRuntime, RuntimeResult
from .self_audit import SelfAuditor
from .spine import EvidenceSpine
from .surface import FailureSurface, SurfaceMapper
from .threat import ThreatCase, ThreatEngine
from .witness import WitnessEnvelope, witness

__all__ = [
    "CandidateTest", "ClaimCompiler", "ClaimLineage", "DependencyGraph",
    "EpistemicState", "EvidenceBridge", "EvidenceRuntime", "EvidenceSpine",
    "FailureSurface", "Falsifier", "Invariant", "InvariantBattery", "Mutation",
    "MutationRegistry", "OptimizationDecision", "PromotionResult", "Relation",
    "FailureClass", "RecoveryAlternative", "RecoveryBudget", "RecoveryDecision",
    "RecoveryEngine", "RecoveryReceipt", "RecoveryState",
    "RuntimeResult", "SelfAuditor", "SurfaceMapper", "TestSelector",
    "ThreatCase", "ThreatEngine", "WitnessEnvelope", "WitnessFederation",
    "promote", "witness",
]

__version__ = "0.3.0"
