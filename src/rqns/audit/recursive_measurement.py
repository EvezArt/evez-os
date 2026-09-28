"""Evidence-bound recursive measurement and audit-of-auditor controls."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


class EvidenceState(str, Enum):
    UNKNOWN = "UNKNOWN"
    PROPOSED = "PROPOSED"
    SUPPORTED = "SUPPORTED"
    VERIFIED = "VERIFIED"
    CONTRADICTED = "CONTRADICTED"
    RETRACTED = "RETRACTED"


class CausalType(str, Enum):
    INTENTION_ARTIFACT = "INTENTION_ARTIFACT"
    ARTIFACT_EXECUTION = "ARTIFACT_EXECUTION"
    EXECUTION_OBSERVATION = "EXECUTION_OBSERVATION"
    MEASUREMENT_INTERPRETATION = "MEASUREMENT_INTERPRETATION"
    TEMPORAL = "TEMPORAL"
    PROVENANCE = "PROVENANCE"
    CAUSAL = "CAUSAL"
    OBSERVER_EFFECT = "OBSERVER_EFFECT"
    SELF_MODEL = "SELF_MODEL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Discrepancy:
    between: Tuple[str, str]
    causal_type: CausalType
    statement: str
    evidence_refs: Tuple[str, ...] = ()
    state: EvidenceState = EvidenceState.UNKNOWN


@dataclass(frozen=True)
class Residual:
    residual_id: str
    observation: str
    expectation: str
    question: str
    candidate_variable: str
    evidence_refs: Tuple[str, ...] = ()
    state: EvidenceState = EvidenceState.UNKNOWN


@dataclass
class GenerationTrace:
    generation: str
    intention: Any
    artifact: Any
    execution: Any
    observation: Any
    source_refs: List[str] = field(default_factory=list)
    reproducible_transform_refs: List[str] = field(default_factory=list)
    discrepancies: List[Discrepancy] = field(default_factory=list)
    residuals: List[Residual] = field(default_factory=list)
    model_revision: Optional[str] = None
    parent_generation: Optional[str] = None
    parent_hash: Optional[str] = None

    def canonical_bytes(self) -> bytes:
        payload = asdict(self)
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()

    def content_hash(self) -> str:
        return sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class ModelDivergence:
    generation: str
    dimensions: Mapping[str, str]
    changed_dimensions: Tuple[str, ...] = ()


@dataclass(frozen=True)
class AuditSeal:
    generation_count: int
    head_hash: Optional[str]
    manifest_hash: str


class RecursiveAuditor:
    """Build a hash-linked genealogy of model/system discrepancies.

    The audit seal makes the auditor itself auditable. Without an external
    commitment, a mutable last record could be rewritten while the chain still
    appears internally consistent.
    """

    def __init__(self) -> None:
        self.generations: List[GenerationTrace] = []
        self.divergence_history: List[ModelDivergence] = []
        self._seal: Optional[AuditSeal] = None

    @property
    def latest(self) -> Optional[GenerationTrace]:
        return self.generations[-1] if self.generations else None

    def add_generation(
        self,
        *,
        generation: str,
        intention: Any,
        artifact: Any,
        execution: Any,
        observation: Any,
        source_refs: Optional[Iterable[str]] = None,
        reproducible_transform_refs: Optional[Iterable[str]] = None,
        discrepancies: Optional[Iterable[Discrepancy]] = None,
        residuals: Optional[Iterable[Residual]] = None,
        model_revision: Optional[str] = None,
    ) -> GenerationTrace:
        if self._seal is not None:
            raise RuntimeError("audit is sealed; append a new auditor instance for a new epoch")
        parent = self.latest
        trace = GenerationTrace(
            generation=generation,
            intention=intention,
            artifact=artifact,
            execution=execution,
            observation=observation,
            source_refs=list(source_refs or ()),
            reproducible_transform_refs=list(reproducible_transform_refs or ()),
            discrepancies=list(discrepancies or ()),
            residuals=list(residuals or ()),
            model_revision=model_revision,
            parent_generation=parent.generation if parent else None,
            parent_hash=parent.content_hash() if parent else None,
        )
        self.generations.append(trace)
        return trace

    @staticmethod
    def claim_state(*, has_observation: bool, has_source: bool, has_reproducible_transform: bool,
                    contradiction: bool = False) -> EvidenceState:
        if contradiction:
            return EvidenceState.CONTRADICTED
        if not has_observation or not has_source:
            return EvidenceState.UNKNOWN
        if not has_reproducible_transform:
            return EvidenceState.SUPPORTED
        return EvidenceState.VERIFIED

    def compare_models(
        self,
        generation: str,
        intended: Mapping[str, Any],
        behavior: Mapping[str, Any],
    ) -> ModelDivergence:
        keys = sorted(set(intended) | set(behavior))
        dimensions: Dict[str, str] = {}
        changed: List[str] = []
        for key in keys:
            left = intended.get(key, "<ABSENT>")
            right = behavior.get(key, "<ABSENT>")
            if left == right:
                dimensions[key] = "MATCH"
            else:
                dimensions[key] = f"INTENDED={left!r}; BEHAVIOR={right!r}"
                changed.append(key)
        result = ModelDivergence(generation, dimensions, tuple(changed))
        self.divergence_history.append(result)
        return result

    def verify_chain(self) -> bool:
        previous_hash: Optional[str] = None
        for trace in self.generations:
            if trace.parent_hash != previous_hash:
                return False
            previous_hash = trace.content_hash()
        return True

    def _manifest_bytes(self) -> bytes:
        payload = {
            "generations": [asdict(trace) for trace in self.generations],
            "divergence_history": [asdict(item) for item in self.divergence_history],
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()

    def seal(self) -> AuditSeal:
        if not self.verify_chain():
            raise ValueError("cannot seal an invalid generation chain")
        seal = AuditSeal(
            generation_count=len(self.generations),
            head_hash=self.latest.content_hash() if self.latest else None,
            manifest_hash=sha256(self._manifest_bytes()).hexdigest(),
        )
        self._seal = seal
        return seal

    def verify_seal(self, seal: Optional[AuditSeal] = None) -> bool:
        expected = seal or self._seal
        if expected is None or not self.verify_chain():
            return False
        current_head = self.latest.content_hash() if self.latest else None
        return (
            expected.generation_count == len(self.generations)
            and expected.head_hash == current_head
            and expected.manifest_hash == sha256(self._manifest_bytes()).hexdigest()
        )

    def export_jsonl(self) -> str:
        return "\n".join(
            json.dumps(asdict(trace), sort_keys=True, default=str)
            for trace in self.generations
        )


__all__ = [
    "AuditSeal",
    "CausalType",
    "Discrepancy",
    "EvidenceState",
    "GenerationTrace",
    "ModelDivergence",
    "RecursiveAuditor",
    "Residual",
]
