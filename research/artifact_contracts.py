# SPDX-License-Identifier: MIT
#!/usr/bin/env python3
"""Deterministic .evez artifact and .evex exchange contracts."""

from __future__ import annotations

import hashlib
import json
from typing import Any

EVEZ_STATES = {
    "UNKNOWN", "PROPOSED", "CLAIMED", "OBSERVED", "MEASURED",
    "REPLICATED", "EXPLAINED", "VERIFIED", "REJECTED",
}
EVEX_ACTIONS = {"READ", "VALIDATE", "VERIFY", "COMPOUND", "AUTHORIZE", "ACT"}


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def build_evez(
    *,
    artifact_id: str,
    artifact_type: str,
    state: str,
    body: Any,
    parents: tuple[str, ...] = (),
    provenance: tuple[str, ...] = (),
) -> dict[str, Any]:
    if not artifact_id or not artifact_type:
        raise ValueError("artifact identity is required")
    if state not in EVEZ_STATES:
        raise ValueError("invalid EVEZ state")
    unsigned = {
        "schema": "evez-artifact-v1",
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "state": state,
        "parents": list(parents),
        "provenance": list(provenance),
        "body": body,
    }
    unsigned["sha256"] = digest(unsigned)
    return unsigned


def verify_evez(document: dict[str, Any]) -> dict[str, Any]:
    required = {"schema", "artifact_id", "artifact_type", "state", "parents", "provenance", "body", "sha256"}
    missing = sorted(required.difference(document))
    if missing:
        return {"verified": False, "error": "missing_fields", "missing": missing}
    if document["schema"] != "evez-artifact-v1":
        return {"verified": False, "error": "schema"}
    if document["state"] not in EVEZ_STATES:
        return {"verified": False, "error": "state"}
    unsigned = {key: document[key] for key in document if key != "sha256"}
    expected = digest(unsigned)
    return {
        "verified": document["sha256"] == expected,
        "expected_sha256": expected,
        "actual_sha256": document["sha256"],
    }


def build_evex(
    *,
    envelope_id: str,
    action: str,
    sender: str,
    payload: Any,
    correlation_id: str,
    authorization_required: bool,
    provenance: tuple[str, ...] = (),
) -> dict[str, Any]:
    if action not in EVEX_ACTIONS:
        raise ValueError("invalid EVEX action")
    if action in {"AUTHORIZE", "ACT"} and not authorization_required:
        raise ValueError("consequential EVEX actions must declare authorization")
    unsigned = {
        "schema": "evex-envelope-v1",
        "envelope_id": envelope_id,
        "action": action,
        "sender": sender,
        "correlation_id": correlation_id,
        "authorization_required": authorization_required,
        "provenance": list(provenance),
        "payload": payload,
    }
    unsigned["sha256"] = digest(unsigned)
    return unsigned


def verify_evex(document: dict[str, Any]) -> dict[str, Any]:
    required = {
        "schema", "envelope_id", "action", "sender", "correlation_id",
        "authorization_required", "provenance", "payload", "sha256",
    }
    missing = sorted(required.difference(document))
    if missing:
        return {"verified": False, "error": "missing_fields", "missing": missing}
    if document["schema"] != "evex-envelope-v1":
        return {"verified": False, "error": "schema"}
    action = document["action"]
    if action not in EVEX_ACTIONS:
        return {"verified": False, "error": "action"}
    if action in {"AUTHORIZE", "ACT"} and not document["authorization_required"]:
        return {"verified": False, "error": "authorization_boundary"}
    unsigned = {key: document[key] for key in document if key != "sha256"}
    expected = digest(unsigned)
    return {
        "verified": document["sha256"] == expected,
        "expected_sha256": expected,
        "actual_sha256": document["sha256"],
    }
