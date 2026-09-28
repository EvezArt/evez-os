"""Evidence-bound self-probe for the assistant/reasoning process.

This does not inspect hidden chain-of-thought. It measures only explicit,
observable commitments: claims, tests, evidence requirements, falsifiers,
and whether the system distinguishes observation from interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class SelfProbeResult:
    subject: str
    claim: str
    observable: str
    test: str
    falsifier: str
    current_state: str
    unresolved: Tuple[str, ...]


def probe_current_reasoning() -> SelfProbeResult:
    return SelfProbeResult(
        subject="assistant reasoning process",
        claim="The response can be made more precise by converting its own proposed mechanisms into explicit, testable artifacts.",
        observable="A concrete repository change contains a callable mechanism plus tests that reject missing evidence requirements.",
        test="Inspect the changed source and test files; run the repository test suite when an execution environment is available.",
        falsifier="The mechanism cannot be inspected, the tests accept an untestable transition, or the claimed change is absent from the branch.",
        current_state="SUPPORTED",
        unresolved=(
            "No runtime test execution is claimed from the GitHub connector alone.",
            "No claim is made about hidden internal reasoning or consciousness.",
            "The self-probe measures explicit artifacts, not private chain-of-thought.",
        ),
    )


__all__ = ["SelfProbeResult", "probe_current_reasoning"]
