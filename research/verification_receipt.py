#!/usr/bin/env python3
"""Deterministic verification receipts for EVEZ promotion decisions.

A receipt provides integrity and binding metadata for a verification observation.
It is NOT a digital signature and does not establish that the named verifier is
trustworthy. Signature/authenticity remains a separate authority layer.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


REQUIRED_FIELDS = {
    "schema",
    "candidate_commit",
    "workflow",
    "run_id",
    "status",
    "target_url",
    "required_checks",
    "observed_checks",
}


def canonical(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def receipt_digest(receipt: Mapping[str, Any]) -> str:
    unsigned = {key: value for key, value in receipt.items() if key != "digest_sha256"}
    return hashlib.sha256(canonical(unsigned)).hexdigest()


def make_receipt(
    *,
    candidate_commit: str,
    workflow: str,
    run_id: str,
    status: str,
    target_url: str,
    required_checks: list[str],
    observed_checks: list[dict[str, str]],
) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema": "evez-verification-receipt-v1",
        "candidate_commit": candidate_commit,
        "workflow": workflow,
        "run_id": run_id,
        "status": status,
        "target_url": target_url,
        "required_checks": list(required_checks),
        "observed_checks": list(observed_checks),
    }
    receipt["digest_sha256"] = receipt_digest(receipt)
    return receipt


def verify_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []

    missing = sorted(REQUIRED_FIELDS.difference(receipt))
    if missing:
        reasons.append("missing fields: " + ",".join(missing))

    supplied = receipt.get("digest_sha256")
    if not isinstance(supplied, str) or not supplied:
        reasons.append("digest_sha256 is absent")
    elif supplied != receipt_digest(receipt):
        reasons.append("digest_sha256 mismatch")

    if receipt.get("schema") != "evez-verification-receipt-v1":
        reasons.append("unsupported receipt schema")

    if receipt.get("status") not in {"success", "failure"}:
        reasons.append("invalid receipt status")

    if not isinstance(receipt.get("required_checks"), list):
        reasons.append("required_checks must be a list")

    if not isinstance(receipt.get("observed_checks"), list):
        reasons.append("observed_checks must be a list")

    return {"valid": not reasons, "reasons": reasons}
