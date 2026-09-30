"""EVEZ Evidence Runtime.

Executable epistemic/adversarial harness for bounded synthetic testing.
"""

from .compiler import ClaimCompiler
from .dependencies import DependencyGraph
from .failure import FailureClassification, FailureClassifier, FailureObservation, FailureSignal
from .decision import NextAction, OperationalDecision, OperationalPlanner
from .epistemics import ClaimLineage, Falsifier, PromotionResult, promote
from .federation import WitnessFederation
from .integration_bridge import EvidenceBridge
from .invariants import Invariant, InvariantBattery
from .ontology import EpistemicState, Relation
from .optimizer import CandidateTest, OptimizationDecision, TestSelector
from .maps import MapKind, MapSpec, UniversalMapRegistry
from .reconcile import MapReconciliation, MapReconciler, ReconciliationState
from .invention import CrossMapInventionEngine, Invention, InventionState, Transformation, CompatibilityResult
from .registry import Mutation, MutationRegistry
from .recovery import FailureClass, RecoveryAlternative, RecoveryBudget, RecoveryCatalog, RecoveryCoordinator, RecoveryDecision, RecoveryEngine, RecoveryReceipt, RecoveryState, RecoveryWitness
from .runtime import EvidenceRuntime, RuntimeResult
from .self_audit import SelfAuditor
from .spine import EvidenceSpine
from .surface import FailureSurface, SurfaceMapper
from .threat import ThreatCase, ThreatEngine
from .witness import WitnessEnvelope, witness

__all__ = [
    "CandidateTest", "ClaimCompiler", "ClaimLineage", "DependencyGraph",
    "EpistemicState", "EvidenceBridge", "EvidenceRuntime", "EvidenceSpine",
    "NextAction", "OperationalDecision", "OperationalPlanner",
    "FailureSurface", "FailureClass", "Falsifier", "Invariant", "InvariantBattery", "Mutation",
    "MutationRegistry", "MapKind", "MapSpec", "UniversalMapRegistry", "OptimizationDecision", "PromotionResult", "Relation",
    "RecoveryAlternative", "RecoveryBudget", "RecoveryCatalog", "RecoveryCoordinator",
    "RecoveryDecision", "RecoveryEngine", "RecoveryReceipt", "RecoveryState", "RecoveryWitness",
    "RuntimeResult", "SelfAuditor", "SurfaceMapper", "TestSelector",
    "ThreatCase", "ThreatEngine", "WitnessEnvelope", "WitnessFederation",
    "promote", "witness",
]

__version__ = "0.4.0"
