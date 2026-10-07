#!/usr/bin/env python3
"""Fail-closed evidence promotion gate for EVEZ research artifacts.

The gate separates model output from measured and replicated evidence. It never
performs deployment, merge, privilege changes, or secret handling.

A CI assertion is accepted only when it is bound to the exact candidate commit.
This prevents a valid result from one revision from accidentally promoting a
different revision.
"""

from __future__ import annotations

import argparse
import json
from typing import Any


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
