"""Offline conformance primitives for the EVEZ Possibility–Witness Loop.

This module checks protocol fixtures and policy decisions only. It does not invoke
remote tools, authenticate identities, or claim live integration.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from typing import Any, Iterable
from urllib.parse import urlparse

PROTOCOL = "EVEZ-Handoff/1"
RISK_LEVELS = {"R0", "R1", "R2", "R3", "R4"}
HANDOFF_STATUSES = {"requested", "accepted", "rejected", "running", "succeeded", "failed", "cancelled", "expired"}
EPISTEMIC_STATES = {"VERIFIED", "SUPPORTED", "INFERRED", "PROPOSED", "UNKNOWN", "STALE", "CONTRADICTED", "RETRACTED"}
TERMINAL_SUCCESS = {"SUCCEEDED", "REPRODUCED"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
TOP_LEVEL_KEYS = {
    "protocol", "task_id", "correlation_id", "created_at", "expires_at",
    "origin", "recipient", "intent", "summary", "constraints",
    "requested_capabilities", "risk_class", "artifacts", "acceptance_criteria",
    "approval_required", "idempotency_key", "status",
}
ARTIFACT_KEYS = {"uri", "media_type", "sha256"}
IDENTITY_KEYS = {"provider", "agent_id"}


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def canonical_json_bytes(value: Any) -> bytes:
    """Deterministic Python JSON representation for local fixtures, not RFC 8785."""
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text.encode("utf-8")


def digest_json(value: Any) -> str:
    return sha256(canonical_json_bytes(value)).hexdigest()


def validate_handoff(envelope: Any, *, now: datetime | None = None) -> list[str]:
    """Return validation errors; an empty list means the fixture passed this local contract."""
    errors: list[str] = []
    if not isinstance(envelope, dict):
        return ["envelope must be an object"]
    missing = sorted(TOP_LEVEL_KEYS - set(envelope))
    extra = sorted(set(envelope) - TOP_LEVEL_KEYS)
    if missing:
        errors.append("missing top-level keys: " + ", ".join(missing))
    if extra:
        errors.append("unknown top-level keys: " + ", ".join(extra))
    if envelope.get("protocol") != PROTOCOL:
        errors.append("unsupported protocol")
    for key in ("task_id", "correlation_id", "intent", "summary", "idempotency_key"):
        if not isinstance(envelope.get(key), str) or not envelope[key].strip():
            errors.append(f"{key} must be a non-empty string")

    created = _parse_time(envelope.get("created_at"))
    expires = _parse_time(envelope.get("expires_at"))
    if created is None:
        errors.append("created_at must be an ISO-8601 timestamp with timezone")
    if expires is None:
        errors.append("expires_at must be an ISO-8601 timestamp with timezone")
    if created is not None and expires is not None:
        if expires <= created:
            errors.append("expires_at must be later than created_at")
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None or current.utcoffset() is None:
            errors.append("validation clock must be timezone-aware")
        elif created > current.astimezone(timezone.utc):
            errors.append("handoff is not yet valid")
        elif expires <= current.astimezone(timezone.utc):
            errors.append("handoff is expired")

    for key in ("origin", "recipient"):
        identity = envelope.get(key)
        if not isinstance(identity, dict):
            errors.append(f"{key} must be an object")
            continue
        if set(identity) != IDENTITY_KEYS:
            errors.append(f"{key} must contain exactly provider and agent_id")
        for field in IDENTITY_KEYS:
            if not isinstance(identity.get(field), str) or not identity[field].strip():
                errors.append(f"{key}.{field} must be a non-empty string")

    for key in ("constraints", "requested_capabilities", "acceptance_criteria"):
        value = envelope.get(key)
        if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
            errors.append(f"{key} must be an array of non-empty strings")
    if envelope.get("risk_class") not in RISK_LEVELS:
        errors.append("risk_class must be R0 through R4")
    if envelope.get("status") not in HANDOFF_STATUSES:
        errors.append("unsupported handoff status")
    if not isinstance(envelope.get("approval_required"), bool):
        errors.append("approval_required must be boolean")

    artifacts = envelope.get("artifacts")
    if not isinstance(artifacts, list):
        errors.append("artifacts must be an array")
    else:
        for index, artifact in enumerate(artifacts):
            prefix = f"artifacts[{index}]"
            if not isinstance(artifact, dict):
                errors.append(f"{prefix} must be an object")
                continue
            if set(artifact) != ARTIFACT_KEYS:
                errors.append(f"{prefix} must contain exactly uri, media_type, sha256")
            uri = artifact.get("uri")
            if not isinstance(uri, str) or not urlparse(uri).scheme:
                errors.append(f"{prefix}.uri must be an absolute URI")
            if not isinstance(artifact.get("media_type"), str) or "/" not in artifact["media_type"]:
                errors.append(f"{prefix}.media_type must be a media type")
            if not isinstance(artifact.get("sha256"), str) or not HEX64.fullmatch(artifact["sha256"]):
                errors.append(f"{prefix}.sha256 must be 64 lowercase hexadecimal characters")
    return errors


def authorize_handoff(
    envelope: dict[str, Any],
    *,
    recipient: dict[str, str],
    granted_capabilities: Iterable[str],
    operation: str = "read",
    read_only: bool = True,
    approval_granted: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Simulate the policy gate; this function never calls a tool or executes the request."""
    errors = validate_handoff(envelope, now=now)
    reasons: list[str] = []
    if errors:
        reasons.append("invalid_handoff")
    if envelope.get("recipient") != recipient:
        reasons.append("recipient_mismatch")
    missing_caps = sorted(set(envelope.get("requested_capabilities", [])) - set(granted_capabilities))
    if missing_caps:
        reasons.append("missing_capabilities:" + ",".join(missing_caps))
    if operation not in {"read", "write"}:
        reasons.append("unsupported_operation")
    if operation == "write" and read_only:
        reasons.append("read_only_mode")
    if envelope.get("risk_class") == "R4":
        reasons.append("risk_R4_denied")
    if envelope.get("approval_required") is True and not approval_granted:
        reasons.append("human_approval_missing")
    if envelope.get("risk_class") == "R3" and envelope.get("approval_required") is not True:
        reasons.append("risk_R3_approval_flag_missing")
    if envelope.get("risk_class") == "R3" and not approval_granted:
        reasons.append("risk_R3_requires_approval")
    allowed = not reasons
    return {
        "decision": "ALLOW" if allowed else "DENY",
        "allowed": allowed,
        "reasons": reasons,
        "missing_capabilities": missing_caps,
        "execution_performed": False,
    }


def verify_artifact_digest(expected_sha256: str, artifact_bytes: bytes) -> bool:
    if not isinstance(expected_sha256, str) or not HEX64.fullmatch(expected_sha256):
        return False
    return sha256(artifact_bytes).hexdigest() == expected_sha256


def can_retry(completed_cycles: int, *, max_cycles: int = 3) -> bool:
    if completed_cycles < 0 or max_cycles < 0:
        return False
    return completed_cycles < max_cycles


def claim_satisfies_state(claim_state: str, required_state: str = "VERIFIED") -> bool:
    """Exact match only: a proposal or inference cannot satisfy a VERIFIED criterion."""
    return claim_state in EPISTEMIC_STATES and claim_state == required_state


def contradiction_record(
    observations: list[dict[str, Any]], *, resolution_test: str
) -> dict[str, Any]:
    """Preserve both (or more) conflicting observations and name a discriminating test."""
    if not isinstance(observations, list) or len(observations) < 2:
        raise ValueError("at least two observations are required")
    if not isinstance(resolution_test, str) or not resolution_test.strip():
        raise ValueError("resolution_test is required")
    copied = deepcopy(observations)
    if any(not isinstance(item, dict) or not item for item in copied):
        raise ValueError("each observation must be a non-empty object")
    return {
        "classification": "CONTRADICTED",
        "observations": copied,
        "resolution_test": resolution_test.strip(),
        "observation_count": len(copied),
    }


def evaluate_witness_receipt(
    receipt: Any, *, required_checks: Iterable[str]
) -> dict[str, Any]:
    """Evaluate a receipt without confusing a claim of success with completed evidence."""
    required = sorted(set(required_checks))
    if not isinstance(receipt, dict) or receipt.get("terminal") is not True:
        return {"status": "blocked", "reason": "missing_terminal_receipt", "checks": {}}
    if receipt.get("result_status") not in TERMINAL_SUCCESS:
        return {"status": "blocked", "reason": "result_not_successful", "checks": receipt.get("checks", {})}
    checks = receipt.get("checks")
    if not isinstance(checks, dict):
        return {"status": "blocked", "reason": "checks_missing", "checks": {}}
    failed = [name for name in required if checks.get(name) != "PASS"]
    if failed:
        return {"status": "blocked", "reason": "required_checks_not_passed", "failed_or_missing_checks": failed, "checks": checks}
    verifier = receipt.get("verifier")
    if not isinstance(verifier, dict) or verifier.get("independent") is not True or not str(verifier.get("identity", "")).strip():
        return {"status": "partially_verified", "reason": "independent_verifier_missing", "checks": checks}
    return {"status": "verified", "reason": "terminal_success_and_required_checks_passed", "checks": checks}


def seal_witness(record: dict[str, Any]) -> dict[str, Any]:
    """Add an integrity digest to a redacted witness record."""
    if not isinstance(record, dict) or "integrity" in record:
        raise ValueError("record must be an object without an existing integrity field")
    sealed = deepcopy(record)
    sealed["integrity"] = {"algorithm": "sha256", "sha256": digest_json(record)}
    return sealed


def verify_sealed_witness(record: Any) -> bool:
    if not isinstance(record, dict):
        return False
    integrity = record.get("integrity")
    if not isinstance(integrity, dict) or integrity.get("algorithm") != "sha256":
        return False
    claimed = integrity.get("sha256")
    payload = {key: value for key, value in record.items() if key != "integrity"}
    return isinstance(claimed, str) and HEX64.fullmatch(claimed) is not None and digest_json(payload) == claimed
