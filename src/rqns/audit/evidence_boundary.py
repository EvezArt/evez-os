"""Explicit boundaries between claims, execution, observation, and independence.

The boundary is deliberately stricter than a provenance record: a claim cannot
be promoted to VERIFIED merely because its own software produced an artifact.
"""

from dataclasses import dataclass, replace
import hashlib
import json
from typing import Optional

from .recursive_measurement import EvidenceState


@dataclass(frozen=True)
class EvidenceBoundary:
    boundary_id: str
    claim_id: str
    source_domain: str
    execution_domain: str
    observation_domain: str
    independent_domain: str
    required_transition: str
    observed_transition: Optional[str]
    failure_mode: Optional[str]
    falsifier: str
    state: EvidenceState = EvidenceState.PROPOSED

    def canonical_bytes(self) -> bytes:
        payload = {
            "boundary_id": self.boundary_id,
            "claim_id": self.claim_id,
            "source_domain": self.source_domain,
            "execution_domain": self.execution_domain,
            "observation_domain": self.observation_domain,
            "independent_domain": self.independent_domain,
            "required_transition": self.required_transition,
            "observed_transition": self.observed_transition,
            "failure_mode": self.failure_mode,
            "falsifier": self.falsifier,
            "state": self.state.value,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def validate_boundary(boundary: EvidenceBoundary) -> str:
    required = (
        boundary.boundary_id,
        boundary.claim_id,
        boundary.source_domain,
        boundary.execution_domain,
        boundary.observation_domain,
        boundary.independent_domain,
        boundary.required_transition,
        boundary.falsifier,
    )
    if not all(required):
        raise ValueError("evidence boundary is incomplete")
    if boundary.state == EvidenceState.VERIFIED:
        if not boundary.observed_transition or not boundary.independent_domain:
            raise ValueError("VERIFIED requires observation and independent domain")
    return boundary.content_hash()


def observe_boundary(
    boundary: EvidenceBoundary,
    observed_transition: str,
    *,
    independently_observed: bool = False,
) -> EvidenceBoundary:
    if not observed_transition:
        raise ValueError("observed transition is required")
    state = (
        EvidenceState.VERIFIED
        if independently_observed
        else EvidenceState.SUPPORTED
    )
    updated = replace(
        boundary,
        observed_transition=observed_transition,
        state=state,
    )
    validate_boundary(updated)
    return updated


def contradict_boundary(boundary: EvidenceBoundary, failure_mode: str) -> EvidenceBoundary:
    if not failure_mode:
        raise ValueError("failure mode is required")
    updated = replace(
        boundary,
        failure_mode=failure_mode,
        state=EvidenceState.CONTRADICTED,
    )
    validate_boundary(updated)
    return updated


__all__ = [
    "EvidenceBoundary",
    "contradict_boundary",
    "observe_boundary",
    "validate_boundary",
]
