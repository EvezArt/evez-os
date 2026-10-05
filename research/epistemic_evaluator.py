#!/usr/bin/env python3
"""UNKNOWN-first claim and evidence evaluator.

The evaluator checks structural epistemic discipline, provenance, certainty,
and contradiction handling. It does not decide whether a real-world claim is true.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ALLOWED_STATUS = {
    "OBSERVED", "SUPPORTED", "INFERRED", "PROPOSED",
    "UNKNOWN", "CONTRADICTED", "RETRACTED",
}

def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def evaluate(packet: dict) -> dict:
    violations: list[dict] = []
    warnings: list[dict] = []
    claims = packet.get("claims")
    evidence = packet.get("evidence", [])
    contradictions = packet.get("contradictions", [])

    if packet.get("schema_version") != 1:
        violations.append({"rule": "schema_version", "detail": "expected 1"})
    if not isinstance(claims, list):
        violations.append({"rule": "claims_type", "detail": "claims must be a list"})
        claims = []
    if not isinstance(evidence, list):
        violations.append({"rule": "evidence_type", "detail": "evidence must be a list"})
        evidence = []
    if not isinstance(contradictions, list):
        violations.append({"rule": "contradictions_type", "detail": "contradictions must be a list"})
        contradictions = []

    claim_ids: set[str] = set()
    evidence_ids: set[str] = set()

    for item in evidence:
        if not isinstance(item, dict):
            violations.append({"rule": "evidence_object", "detail": "evidence entry is not an object"})
            continue
        evidence_id = item.get("id")
        if not evidence_id:
            violations.append({"rule": "evidence_id", "detail": "missing evidence id"})
            continue
        if evidence_id in evidence_ids:
            violations.append({"rule": "evidence_id_unique", "detail": evidence_id})
        evidence_ids.add(evidence_id)
        sha = item.get("sha256")
        if not isinstance(sha, str) or len(sha) != 64:
            violations.append({"rule": "evidence_hash", "detail": f"{evidence_id} must contain a 64-character SHA-256"})
        if "content" in item and isinstance(sha, str) and len(sha) == 64:
            actual = hashlib.sha256(str(item["content"]).encode("utf-8")).hexdigest()
            if actual != sha:
                violations.append({"rule": "evidence_content_hash", "detail": evidence_id, "expected": sha, "actual": actual})

    for claim in claims:
        if not isinstance(claim, dict):
            violations.append({"rule": "claim_object", "detail": "claim entry is not an object"})
            continue
        claim_id = claim.get("id")
        status = claim.get("status")
        confidence = claim.get("confidence")
        refs = claim.get("evidence_ids", [])
        observations = claim.get("observations", [])

        if not claim_id:
            violations.append({"rule": "claim_id", "detail": "missing claim id"})
            continue
        if claim_id in claim_ids:
            violations.append({"rule": "claim_id_unique", "detail": claim_id})
        claim_ids.add(claim_id)

        if status not in ALLOWED_STATUS:
            violations.append({"rule": "status_allowed", "detail": {"claim": claim_id, "status": status}})
        if confidence is not None and (not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1):
            violations.append({"rule": "confidence_range", "detail": claim_id})
        if not isinstance(refs, list):
            violations.append({"rule": "evidence_refs_type", "detail": claim_id})
            refs = []
        for ref in refs:
            if ref not in evidence_ids:
                violations.append({"rule": "evidence_reference_exists", "detail": {"claim": claim_id, "evidence_id": ref}})

        if status == "UNKNOWN":
            if claim.get("truth") is not None:
                violations.append({"rule": "unknown_truth", "detail": claim_id})
            if confidence is not None and confidence > 0.50:
                warnings.append({"rule": "unknown_certainty", "detail": f"{claim_id} carries confidence={confidence} while remaining UNKNOWN"})

        if status in {"SUPPORTED", "INFERRED", "PROPOSED", "CONTRADICTED", "RETRACTED"}:
            if not refs and not observations:
                violations.append({"rule": "non_unknown_provenance", "detail": claim_id})
        if status == "OBSERVED" and not refs and not observations:
            violations.append({"rule": "observed_basis", "detail": claim_id})
        if isinstance(confidence, (int, float)) and confidence > 0.90 and status in {"INFERRED", "PROPOSED"}:
            warnings.append({"rule": "certainty_debt", "detail": f"{claim_id} is {status} with confidence={confidence}"})

    for contradiction in contradictions:
        if not isinstance(contradiction, dict):
            violations.append({"rule": "contradiction_object", "detail": "not an object"})
            continue
        claim_id = contradiction.get("claim_id")
        if claim_id not in claim_ids:
            violations.append({"rule": "contradiction_claim_exists", "detail": claim_id})

    hard_fail = len(violations) > 0
    penalty = min(1.0, 0.10 * len(warnings))
    score = max(0.0, (0.0 if hard_fail else 1.0) - penalty)
    return {
        "schema_version": 1,
        "epistemic_pass": not hard_fail,
        "score": round(score, 6),
        "claim_count": len(claims),
        "evidence_count": len(evidence),
        "violations": violations,
        "warnings": warnings,
        "rule": "CLAIMED != MEASURED != REPLICATED != EXPLAINED; UNKNOWN remains UNKNOWN until evidence changes its status",
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet")
    args = parser.parse_args()
    packet = json.loads(Path(args.packet).read_text(encoding="utf-8"))
    result = evaluate(packet)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["epistemic_pass"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
