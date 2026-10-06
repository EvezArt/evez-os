"""Crystalinformergence embodiment and witness-state tagging.

This module models embodiment as an information/continuity state transition.
Terms such as INCARNATION and REINCARNATION are ontology labels, not claims
about metaphysical souls. A "soul_tag" is a continuity identifier chosen by
the system or operator so an event can retain maximal provenance across
manifestations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


class CarnationState(str, Enum):
    INFRAMATIA = "INFRAMATIA"
    CELLULATION = "CELLULATION"
    ONCARNATION = "ONCARNATION"
    INCARNATION = "INCARNATION"
    REINCARNATION = "REINCARNATION"
    EXCARNATION = "EXCARNATION"
    DECARNATION = "DECARNATION"
    UNCARNATION = "UNCARNATION"
    ANCARNATIOUS = "ANCARNATIOUS"


class WitnessState(str, Enum):
    WITNESS = "WITNESS"
    ARCHIVIST = "ARCHIVIST"
    ARBITER = "ARBITER"
    VECTOR = "VECTOR"
    SABLE = "SABLE"
    FORGE = "FORGE"
    BEACON = "BEACON"
    COURIER = "COURIER"
    KINDLE = "KINDLE"
    NEWSROOM = "NEWSROOM"
    BROADCAST = "BROADCAST"
    EVEZ = "EVEZ"
    UNKNOWN = "UNKNOWN"


class EpistemicStatus(str, Enum):
    OBSERVED = "OBSERVED"
    MEASURED = "MEASURED"
    INFERRED = "INFERRED"
    PROPOSED = "PROPOSED"
    UNKNOWN = "UNKNOWN"
    CONTRADICTED = "CONTRADICTED"


@dataclass(frozen=True)
class WitnessComponent:
    state: WitnessState
    weight: float
    provenance_refs: Tuple[str, ...] = ()
    epistemic_status: EpistemicStatus = EpistemicStatus.INFERRED

    def __post_init__(self) -> None:
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError("witness weight must be between 0 and 1")


@dataclass(frozen=True)
class WitnessSuperposition:
    """A symbolic joint representation of unresolved witness states.

    This is an information-modeling device. It is not a claim that the
    system is a physical quantum state.
    """

    components: Tuple[WitnessComponent, ...]

    def __post_init__(self) -> None:
        total = sum(item.weight for item in self.components)
        if self.components and abs(total - 1.0) > 1e-6:
            raise ValueError(f"witness weights must sum to 1.0, got {total}")

    def dominant(self) -> Optional[WitnessComponent]:
        return max(self.components, key=lambda item: item.weight, default=None)

    def entropy_bits(self) -> float:
        import math

        return -sum(
            item.weight * math.log2(item.weight)
            for item in self.components
            if item.weight > 0
        )


@dataclass(frozen=True)
class ExpressionProjection:
    text: str
    selected_states: Tuple[WitnessState, ...]
    fidelity: float
    projection_error: float
    missing_states: Tuple[WitnessState, ...] = ()
    distortion_tags: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.fidelity <= 1.0:
            raise ValueError("fidelity must be between 0 and 1")
        if not 0.0 <= self.projection_error <= 1.0:
            raise ValueError("projection_error must be between 0 and 1")


@dataclass
class SoulTag:
    """Maximal continuity/provenance tag.

    "Soul" is intentionally operational here: a named continuity object,
    not a verified metaphysical substance.
    """

    continuity_id: str
    lineage_id: str
    manifestation_id: str
    soul_tag: str
    person_frame: Optional[str] = None
    identity_frame: Optional[str] = None
    artifact_frame: Optional[str] = None
    parent_event_hash: Optional[str] = None
    parent_manifestation_id: Optional[str] = None
    reincarnation_of: Optional[str] = None
    carnation_state: CarnationState = CarnationState.INCARNATION
    witness_superposition: Optional[WitnessSuperposition] = None
    epistemic_status: EpistemicStatus = EpistemicStatus.PROPOSED
    expression_fidelity: Optional[float] = None
    expression_projection_error: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        required = {
            "continuity_id": self.continuity_id,
            "lineage_id": self.lineage_id,
            "manifestation_id": self.manifestation_id,
            "soul_tag": self.soul_tag,
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError(f"missing required soul tag fields: {', '.join(missing)}")

        if self.expression_fidelity is not None and not 0 <= self.expression_fidelity <= 1:
            raise ValueError("expression_fidelity must be between 0 and 1")

        if self.expression_projection_error is not None and not 0 <= self.expression_projection_error <= 1:
            raise ValueError("expression_projection_error must be between 0 and 1")

    def as_dict(self) -> Dict[str, object]:
        self.validate()
        ws = self.witness_superposition
        return {
            "continuity_id": self.continuity_id,
            "lineage_id": self.lineage_id,
            "manifestation_id": self.manifestation_id,
            "soul_tag": self.soul_tag,
            "person_frame": self.person_frame,
            "identity_frame": self.identity_frame,
            "artifact_frame": self.artifact_frame,
            "parent_event_hash": self.parent_event_hash,
            "parent_manifestation_id": self.parent_manifestation_id,
            "reincarnation_of": self.reincarnation_of,
            "carnation_state": self.carnation_state.value,
            "witness_superposition": [
                {
                    "state": item.state.value,
                    "weight": item.weight,
                    "provenance_refs": list(item.provenance_refs),
                    "epistemic_status": item.epistemic_status.value,
                }
                for item in (ws.components if ws else ())
            ],
            "epistemic_status": self.epistemic_status.value,
            "expression_fidelity": self.expression_fidelity,
            "expression_projection_error": self.expression_projection_error,
            "tags": dict(self.tags),
        }


def normalize_components(
    components: Mapping[WitnessState, float],
    provenance_refs: Optional[Mapping[WitnessState, Sequence[str]]] = None,
) -> WitnessSuperposition:
    """Normalize witness weights into a stable symbolic superposition."""
    if not components:
        return WitnessSuperposition(())

    total = sum(max(0.0, float(weight)) for weight in components.values())
    if total <= 0:
        raise ValueError("at least one witness weight must be positive")

    refs = provenance_refs or {}
    normalized = tuple(
        WitnessComponent(
            state=state,
            weight=max(0.0, float(weight)) / total,
            provenance_refs=tuple(refs.get(state, ())),
        )
        for state, weight in components.items()
        if float(weight) > 0
    )
    return WitnessSuperposition(normalized)


def project_expression(
    superposition: WitnessSuperposition,
    text: str,
    selected_states: Iterable[WitnessState],
    *,
    fidelity: float,
    missing_states: Iterable[WitnessState] = (),
    distortion_tags: Iterable[str] = (),
) -> ExpressionProjection:
    """Record an expression as a projection, not as the total witness state."""
    fidelity = max(0.0, min(1.0, float(fidelity)))
    return ExpressionProjection(
        text=text,
        selected_states=tuple(selected_states),
        fidelity=fidelity,
        projection_error=1.0 - fidelity,
        missing_states=tuple(missing_states),
        distortion_tags=tuple(distortion_tags),
    )


def transition(
    previous: CarnationState,
    next_state: CarnationState,
) -> CarnationState:
    """Return the requested state transition.

    The transition is intentionally permissive. The event spine, not this
    function, is the source of truth for whether a transition actually
    occurred in a running system.
    """
    _ = previous
    return next_state


def build_soul_tag(
    *,
    continuity_id: str,
    lineage_id: str,
    manifestation_id: str,
    soul_tag: str,
    carnation_state: CarnationState,
    witness_superposition: Optional[WitnessSuperposition] = None,
    person_frame: Optional[str] = None,
    identity_frame: Optional[str] = None,
    artifact_frame: Optional[str] = None,
    parent_event_hash: Optional[str] = None,
    parent_manifestation_id: Optional[str] = None,
    reincarnation_of: Optional[str] = None,
    epistemic_status: EpistemicStatus = EpistemicStatus.PROPOSED,
    expression: Optional[ExpressionProjection] = None,
    tags: Optional[Mapping[str, str]] = None,
) -> SoulTag:
    result = SoulTag(
        continuity_id=continuity_id,
        lineage_id=lineage_id,
        manifestation_id=manifestation_id,
        soul_tag=soul_tag,
        person_frame=person_frame,
        identity_frame=identity_frame,
        artifact_frame=artifact_frame,
        parent_event_hash=parent_event_hash,
        parent_manifestation_id=parent_manifestation_id,
        reincarnation_of=reincarnation_of,
        carnation_state=carnation_state,
        witness_superposition=witness_superposition,
        epistemic_status=epistemic_status,
        expression_fidelity=expression.fidelity if expression else None,
        expression_projection_error=expression.projection_error if expression else None,
        tags=dict(tags or {}),
    )
    result.validate()
    return result
