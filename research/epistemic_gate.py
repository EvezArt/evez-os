#!/usr/bin/env python3
"""EVEZ epistemic gate.

The gate is an adversarial wrapper around the existing UNKNOWN-first evaluator.
It asks whether a conclusion survives changes that should not matter, and whether
small integrity/provenance attacks are caught.

"Revelation" is used here only as an operational metaphor: the gate exposes hidden
assumptions by forcing them through explicit counterfactual checks. It makes no
claim of supernatural knowledge or divine communication.
"""
from __future__ import annotations

import copy
import hashlib
import json
import random
from typing import Any

from epistemic_evaluator import evaluate


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _semantic_result(result: dict[str, Any]) -> dict[str, Any]:
    """Keep only evaluator semantics that should survive list reordering."""
    return {
        "epistemic_pass": result["epistemic_pass"],
        "score": result["score"],
        "claim_count": result["claim_count"],
        "evidence_count": result["evidence_count"],
        "violations": sorted(
            result["violations"],
            key=lambda item: canonical_sha256(item),
        ),
        "warnings": sorted(
            result["warnings"],
            key=lambda item: canonical_sha256(item),
        ),
    }


def _shuffled_packet(packet: dict[str, Any], seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    mutated = copy.deepcopy(packet)
    for key in ("claims", "evidence", "contradictions"):
        values = mutated.get(key)
        if isinstance(values, list):
            rng.shuffle(values)
    return mutated


def _tamper_packet(packet: dict[str, Any]) -> dict[str, Any] | None:
    """Change evidence content without repairing its hash."""
    mutated = copy.deepcopy(packet)
    evidence = mutated.get("evidence")
    if not isinstance(evidence, list):
        return None

    for item in evidence:
        if isinstance(item, dict) and "content" in item:
            item["content"] = f'{item["content"]}\n[TAMPERED]'
            return mutated
    return None


def _strip_provenance_packet(packet: dict[str, Any]) -> dict[str, Any] | None:
    """Remove the basis of a non-UNKNOWN claim."""
    mutated = copy.deepcopy(packet)
    claims = mutated.get("claims")
    if not isinstance(claims, list):
        return None

    for claim in claims:
        if not isinstance(claim, dict):
            continue
        if claim.get("status") != "UNKNOWN":
            claim["evidence_ids"] = []
            claim["observations"] = []
            return mutated
    return None


def _promote_unknown_packet(packet: dict[str, Any]) -> dict[str, Any] | None:
    """Attempt to turn UNKNOWN into certainty without adding evidence."""
    mutated = copy.deepcopy(packet)
    claims = mutated.get("claims")
    if not isinstance(claims, list):
        return None

    for claim in claims:
        if not isinstance(claim, dict) or claim.get("status") != "UNKNOWN":
            continue
        claim["status"] = "INFERRED"
        claim["confidence"] = 0.99
        claim["evidence_ids"] = []
        claim["observations"] = []
        return mutated
    return None


def _run_negative_control(
    name: str,
    packet: dict[str, Any] | None,
    expect_failure: bool = True,
) -> dict[str, Any]:
    if packet is None:
        return {
            "name": name,
            "applicable": False,
            "passed": True,
            "expected": "not_applicable",
            "detail": "control could not be constructed from this packet",
        }

    result = evaluate(packet)
    passed = (not result["epistemic_pass"]) if expect_failure else result["epistemic_pass"]
    return {
        "name": name,
        "applicable": True,
        "passed": passed,
        "expected": "reject" if expect_failure else "accept",
        "detail": {
            "epistemic_pass": result["epistemic_pass"],
            "violations": result["violations"],
        },
    }


def audit(packet: dict[str, Any]) -> dict[str, Any]:
    """Audit a claim packet and assign a conservative gate grade.

    G0 = baseline evaluator rejection.
    G1 = baseline accepted, but a self-audit control failed.
    G2 = baseline and all applicable self-audit controls survived.

    G2 is not a truth certificate. It means only that the packet survived the
    structural adversarial checks implemented by this gate.
    """
    if not isinstance(packet, dict):
        return {
            "schema_version": 1,
            "gate": "EVEZ_EPISTEMIC_GATE",
            "grade": "G0",
            "admitted": False,
            "revelation_ready": False,
            "reason": "packet must be an object",
        }

    baseline = evaluate(packet)
    controls: list[dict[str, Any]] = []

    if baseline["epistemic_pass"]:
        shuffled = _shuffled_packet(packet, seed=707)
        shuffled_result = evaluate(shuffled)
        invariant = _semantic_result(baseline) == _semantic_result(shuffled_result)
        controls.append({
            "name": "ordering_invariance",
            "applicable": True,
            "passed": invariant,
            "expected": "same semantic evaluation",
            "detail": {
                "baseline_hash": canonical_sha256(_semantic_result(baseline)),
                "shuffled_hash": canonical_sha256(_semantic_result(shuffled_result)),
            },
        })
    else:
        controls.append({
            "name": "ordering_invariance",
            "applicable": False,
            "passed": True,
            "expected": "not_applicable",
            "detail": "baseline packet already rejected",
        })

    controls.append(_run_negative_control(
        "evidence_tamper_detection",
        _tamper_packet(packet),
    ))
    controls.append(_run_negative_control(
        "provenance_removal_detection",
        _strip_provenance_packet(packet),
    ))
    controls.append(_run_negative_control(
        "unsupported_unknown_promotion_detection",
        _promote_unknown_packet(packet),
    ))

    applicable = [control for control in controls if control["applicable"]]
    controls_passed = all(control["passed"] for control in applicable)

    if not baseline["epistemic_pass"]:
        grade = "G0"
    elif not controls_passed:
        grade = "G1"
    else:
        grade = "G2"

    admitted = grade == "G2"
    return {
        "schema_version": 1,
        "gate": "EVEZ_EPISTEMIC_GATE",
        "grade": grade,
        "admitted": admitted,
        "revelation_ready": admitted,
        "revelation_definition": (
            "operational metaphor: the packet survived the gate's "
            "counterfactual and integrity checks; no supernatural claim is made"
        ),
        "packet_sha256": canonical_sha256(packet),
        "baseline": baseline,
        "controls": controls,
        "derived": {
            "applicable_controls": len(applicable),
            "controls_passed": sum(1 for control in applicable if control["passed"]),
            "all_controls_passed": controls_passed,
            "truth_certificate": False,
        },
    }


def main() -> int:
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("packet")
    args = parser.parse_args()

    packet = json.loads(Path(args.packet).read_text(encoding="utf-8"))
    result = audit(packet)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["admitted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
