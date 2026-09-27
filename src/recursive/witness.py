"""
Independent witness checks for recursive experiment records.

The witness intentionally recomputes integrity properties from the canonical
record instead of trusting values produced by the experiment engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Sequence

from .experiment_protocol import ExperimentRecord


@dataclass(frozen=True)
class WitnessFinding:
    ok: bool
    code: str
    detail: str


def _distance(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("state width mismatch")
    return sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def verify_record(record: ExperimentRecord) -> tuple[WitnessFinding, ...]:
    findings: list[WitnessFinding] = []

    if not record.run_id.strip():
        findings.append(WitnessFinding(False, "MISSING_RUN_ID", "run_id is empty"))

    if len(record.observed_state) != len(record.counterfactual_state):
        findings.append(
            WitnessFinding(
                False,
                "STATE_WIDTH_MISMATCH",
                "observed and counterfactual states differ in width",
            )
        )
    else:
        expected = _distance(record.observed_state, record.counterfactual_state)
        if abs(expected - record.measurement_influence) > 1e-9:
            findings.append(
                WitnessFinding(
                    False,
                    "INFLUENCE_MISMATCH",
                    f"recorded={record.measurement_influence} recomputed={expected}",
                )
            )

    recomputed_hash = record.content_hash()
    if not recomputed_hash:
        findings.append(
            WitnessFinding(False, "HASH_FAILURE", "content hash was empty")
        )

    if not findings:
        findings.append(
            WitnessFinding(True, "RECORD_VALID", "independent checks passed")
        )
    return tuple(findings)


def verify_chain(records: Sequence[ExperimentRecord]) -> tuple[WitnessFinding, ...]:
    findings: list[WitnessFinding] = []
    parent = "genesis"

    for index, record in enumerate(records):
        if record.parent_hash != parent:
            findings.append(
                WitnessFinding(
                    False,
                    "BROKEN_PARENT_CHAIN",
                    f"index={index} expected={parent} actual={record.parent_hash}",
                )
            )

        findings.extend(verify_record(record))
        parent = record.content_hash()

    if not findings:
        findings.append(
            WitnessFinding(True, "CHAIN_VALID", f"{len(records)} records verified")
        )
    elif all(item.ok for item in findings):
        findings.append(
            WitnessFinding(True, "CHAIN_VALID", f"{len(records)} records verified")
        )

    return tuple(findings)
