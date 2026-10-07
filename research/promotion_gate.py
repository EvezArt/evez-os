#!/usr/bin/env python3
"""Fail-closed evidence promotion gate for EVEZ research artifacts.

The gate separates model output from measured and replicated evidence. It never
performs deployment, merge, privilege changes, or secret handling.

CI verification is accepted only when a deterministic verification receipt binds
the exact candidate commit to a successful run and its declared checks.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from research.verification_receipt import verify_receipt


ALLOWED = {"MODEL_ONLY", "MEASURED", "REPLICATED"}


def evaluate(packet: dict[str, Any]) -> dict[str, Any]:
    status = packet.get("status")
    reasons: list[str] = []

    if status not in ALLOWED:
        reasons.append("unknown status")

    provenance = packet.get("provenance", {})
    expected_commit = provenance.get("commit_sha")
    if not expected_commit:
        reasons.append("commit provenance is absent")

    ci = packet.get("ci", {})
    if ci.get("verified") is not True:
        reasons.append("independent CI verification is absent")
    if ci.get("status") != "success":
        reasons.append("CI status is not success")
    if expected_commit and ci.get("commit_sha") != expected_commit:
        reasons.append("CI result is not bound to the candidate commit")

    receipt = ci.get("receipt")
    if not isinstance(receipt, dict):
        reasons.append("verification receipt is absent")
    else:
        receipt_result = verify_receipt(receipt)
        if not receipt_result["valid"]:
            reasons.extend("receipt: " + reason for reason in receipt_result["reasons"])
        if expected_commit and receipt.get("candidate_commit") != expected_commit:
            reasons.append("receipt is not bound to the candidate commit")
        if receipt.get("status") != "success":
            reasons.append("receipt status is not success")
        if not receipt.get("workflow"):
            reasons.append("receipt workflow is absent")
        if not receipt.get("run_id"):
            reasons.append("receipt run_id is absent")
        if not receipt.get("target_url"):
            reasons.append("receipt target_url is absent")
        required_checks = receipt.get("required_checks")
        observed_checks = receipt.get("observed_checks")
        if not isinstance(required_checks, list) or not required_checks:
            reasons.append("receipt required_checks are absent")
        if not isinstance(observed_checks, list):
            reasons.append("receipt observed_checks are absent")
        else:
            observed = {
                item.get("name"): item.get("status")
                for item in observed_checks
                if isinstance(item, dict)
            }
            for check in required_checks if isinstance(required_checks, list) else []:
                if observed.get(check) != "success":
                    reasons.append(f"required check is not successful: {check}")

    if packet.get("uncertainty") is None:
        reasons.append("uncertainty is absent")

    if packet.get("dissent") is None:
        reasons.append("dissent is absent")

    if status in {"MEASURED", "REPLICATED"} and not packet.get("measurement_source"):
        reasons.append("measurement source is absent")

    if status == "REPLICATED" and not packet.get("independent_replication"):
        reasons.append("independent replication evidence is absent")

    return {
        "promotable": not reasons,
        "status": status,
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet")
    args = parser.parse_args()
    with open(args.packet, encoding="utf-8") as handle:
        packet = json.load(handle)
    result = evaluate(packet)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["promotable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
