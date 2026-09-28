"""Controlled representational tunneling over audited residuals.

Metamordia is an operational term for changing representation when a
persistent residual cannot be resolved inside the current frame. It makes no
literal quantum-physics claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Mapping, Tuple


@dataclass(frozen=True)
class MetamordiaTransition:
    transition_id: str
    residual_id: str
    from_frame: str
    to_frame: str
    trigger: str
    expected_distinction: str
    test_ref: str
    falsifier: str
    status: str = "PROPOSED"

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.__dict__, sort_keys=True, separators=(",", ":")).encode()

    def content_hash(self) -> str:
        return sha256(self.canonical_bytes()).hexdigest()


def require_testable_transition(transition: MetamordiaTransition) -> str:
    """Return the transition hash only when the frame change is testable."""
    required = (
        transition.transition_id,
        transition.residual_id,
        transition.from_frame,
        transition.to_frame,
        transition.trigger,
        transition.expected_distinction,
        transition.test_ref,
        transition.falsifier,
    )
    if not all(required):
        raise ValueError("metamordia transition is not testable")
    return transition.content_hash()


def compare_frame_predictions(
    before: Mapping[str, object], after: Mapping[str, object]
) -> Tuple[str, ...]:
    """Return dimensions whose predictions differ across a frame transition."""
    keys = sorted(set(before) | set(after))
    return tuple(key for key in keys if before.get(key) != after.get(key))


__all__ = ["MetamordiaTransition", "compare_frame_predictions", "require_testable_transition"]
