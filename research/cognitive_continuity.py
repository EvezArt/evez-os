#!/usr/bin/env python3
"""Immutable cognitive-temporal continuity and absence ledger primitives."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable

EPISTEMIC_STATES = (
    "UNKNOWN",
    "PROPOSED",
    "CLAIMED",
    "OBSERVED",
    "MEASURED",
    "REPLICATED",
    "EXPLAINED",
    "VERIFIED",
    "REJECTED",
)

ABSENCE_KINDS = (
    "NULL",
    "SUPPRESSED",
    "TOMBSTONED",
    "SUBSTITUTED",
    "CONTRADICTED",
    "TEMPORAL_ORPHAN",
    "LINEAGE_BREAK",
    "ECHO",
    "UNACKNOWLEDGED_UNKNOWN",
    "INDETERMINATE",
)


@dataclass(frozen=True)
class CognitiveNode:
    node_id: str
    timestamp: str
    state: str
    content: Any
    parents: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.node_id or not self.timestamp:
            raise ValueError("node identity and timestamp are required")
        if self.state not in EPISTEMIC_STATES:
            raise ValueError("invalid epistemic state")


@dataclass(frozen=True)
class AbsenceRecord:
    absence_id: str
    timestamp: str
    subject_id: str
    kind: str
    reason: str
    prior_digest: str | None = None
    replacement_id: str | None = None
    evidence: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.absence_id or not self.timestamp or not self.subject_id:
            raise ValueError("absence identity is incomplete")
        if self.kind not in ABSENCE_KINDS:
            raise ValueError("invalid absence kind")
        if self.kind == "SUBSTITUTED" and not self.replacement_id:
            raise ValueError("substitution requires replacement_id")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def node_digest(node: CognitiveNode) -> str:
    node.validate()
    return digest(asdict(node))


def absence_digest(record: AbsenceRecord) -> str:
    record.validate()
    return digest(asdict(record))


def detect_absences(nodes: Iterable[CognitiveNode]) -> list[AbsenceRecord]:
    items = sorted(nodes, key=lambda node: (node.timestamp, node.node_id))
    known = {node.node_id for node in items}
    records: list[AbsenceRecord] = []

    for node in items:
        node.validate()
        missing_parents = [parent for parent in node.parents if parent not in known]
        if missing_parents:
            records.append(
                AbsenceRecord(
                    absence_id=f"orphan:{node.node_id}",
                    timestamp=node.timestamp,
                    subject_id=node.node_id,
                    kind="TEMPORAL_ORPHAN",
                    reason="one or more declared parents are unavailable",
                    evidence=tuple(sorted(missing_parents)),
                )
            )

    for earlier, later in zip(items, items[1:]):
        if earlier.node_id not in later.parents:
            records.append(
                AbsenceRecord(
                    absence_id=f"gap:{earlier.node_id}:{later.node_id}",
                    timestamp=later.timestamp,
                    subject_id=later.node_id,
                    kind="LINEAGE_BREAK",
                    reason="adjacent timeline nodes have no declared continuity edge",
                    prior_digest=node_digest(earlier),
                    evidence=(earlier.node_id,),
                )
            )

    return records


def tombstone(
    subject_id: str,
    *,
    timestamp: str,
    reason: str,
    prior_digest: str | None = None,
) -> AbsenceRecord:
    record = AbsenceRecord(
        absence_id=f"tombstone:{subject_id}:{timestamp}",
        timestamp=timestamp,
        subject_id=subject_id,
        kind="TOMBSTONED",
        reason=reason,
        prior_digest=prior_digest,
    )
    record.validate()
    return record
