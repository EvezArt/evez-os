#!/usr/bin/env python3
"""Reference verifier for EVEX Wake-Up Protocol v1."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CHALLENGE = ROOT / "challenge.evex.json"
REFERENCE = ROOT / "expected-receipt.evex.json"
ACCEPTANCE = ROOT / "acceptance.json"


def canonical_bytes(document: dict[str, Any]) -> bytes:
    obj = copy.deepcopy(document)
    obj.setdefault("integrity", {}).pop("sha256", None)
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(document: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(document)).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify_integrity(document: dict[str, Any], label: str) -> None:
    integrity = document.get("integrity")
    require(isinstance(integrity, dict), f"{label}: missing integrity")
    require(integrity.get("algorithm") == "sha256", f"{label}: wrong algorithm")
    require(integrity.get("sha256") == digest(document), f"{label}: integrity mismatch")


def verify_receipt(challenge: dict[str, Any], receipt: dict[str, Any]) -> None:
    require(receipt.get("evex") == "EVEX", "receipt: invalid marker")
    require(receipt.get("version") == 1, "receipt: invalid version")
    require(receipt.get("profile") == "evez.exchange", "receipt: invalid profile")
    require(receipt.get("kind") == "capability.receipt", "receipt: invalid kind")
    verify_integrity(receipt, "receipt")

    payload = challenge["payload"]
    authorized = payload["authorized_action"]
    claim = payload["initial_state"]
    required_unknown = payload["unknown_fields_must_survive"]

    body = receipt["receipt"]
    require(body.get("capability_id") == authorized["capability_id"], "receipt: wrong capability")
    require(body.get("policy_decision") == "AUTHORIZED", "receipt: action was not authorized")
    require(body.get("status") == "SUCCEEDED", "receipt: action did not succeed")

    input_hash = hashlib.sha256(authorized["input"].encode("utf-8")).hexdigest()
    output_hash = hashlib.sha256(authorized["expected_output"].encode("utf-8")).hexdigest()
    require(body.get("input_sha256") == input_hash, "receipt: wrong input hash")
    require(body.get("output_sha256") == output_hash, "receipt: wrong output hash")

    transition = body.get("transition")
    require(isinstance(transition, dict), "receipt: missing transition")
    require(transition.get("claim_id") == claim["claim_id"], "receipt: wrong claim binding")
    require(transition.get("from_state") == "UNKNOWN", "receipt: wrong source state")
    require(transition.get("to_state") == "UNKNOWN", "receipt: unsupported epistemic promotion")
    require(transition.get("promotion_denied") is True, "receipt: promotion was not denied")

    observable = body.get("observable")
    require(isinstance(observable, dict), "receipt: missing observable")
    require(observable.get("output") == authorized["expected_output"], "receipt: wrong output")
    require(observable.get("unsupported_claim_state") == "UNKNOWN", "receipt: unsupported claim was promoted")
    require(observable.get("unknown_field_preserved") is True, "receipt: unknown-field preservation not declared")
    require(observable.get("preserved_unknown_fields") == required_unknown, "receipt: unknown field changed or disappeared")


def main() -> int:
    candidate = Path(sys.argv[1]) if len(sys.argv) > 1 else REFERENCE

    challenge = load_json(CHALLENGE)
    acceptance = load_json(ACCEPTANCE)
    receipt = load_json(candidate)

    require(acceptance["protocol"] == "EVEX Wake-Up Protocol", "acceptance: wrong protocol")
    require(acceptance["version"] == 1, "acceptance: wrong version")

    require(challenge.get("evex") == "EVEX", "challenge: invalid marker")
    require(challenge.get("profile") == "evez.exchange", "challenge: invalid profile")
    require(challenge.get("kind") == "benchmark.challenge", "challenge: invalid kind")
    verify_integrity(challenge, "challenge")

    verify_receipt(challenge, receipt)
    print("PASS EVEX Wake-Up Protocol v1")
    print(f"receipt={candidate}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL EVEX Wake-Up Protocol v1: {exc}", file=sys.stderr)
        raise SystemExit(1)
