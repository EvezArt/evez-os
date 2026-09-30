"""Epistemic states and explicit status transitions."""
from __future__ import annotations
from enum import StrEnum

class EpistemicState(StrEnum):
    UNKNOWN = "UNKNOWN"
    PROPOSED = "PROPOSED"
    INFERRED = "INFERRED"
    SUPPORTED = "SUPPORTED"
    VERIFIED = "VERIFIED"
    STALE = "STALE"
    CONTRADICTED = "CONTRADICTED"
    RETRACTED = "RETRACTED"

class Relation(StrEnum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    DEPENDS_ON = "DEPENDS_ON"
    OBSERVED_BY = "OBSERVED_BY"
    DERIVED_FROM = "DERIVED_FROM"
    FALSIFIES = "FALSIFIES"

def state_for_classification(classification: str) -> EpistemicState:
    return {
        "PASS": EpistemicState.SUPPORTED,
        "VIOLATION": EpistemicState.CONTRADICTED,
        "CONTRADICTION": EpistemicState.CONTRADICTED,
        "UNKNOWN": EpistemicState.UNKNOWN,
    }.get(classification, EpistemicState.UNKNOWN)
