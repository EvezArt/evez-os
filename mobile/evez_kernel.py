#!/usr/bin/env python3
"""Termux wrapper for the bounded EVEZ execution kernel."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.execution_kernel import plan  # noqa: E402
from research.materium import ResourceBudget, ResourceRequest  # noqa: E402
from research.signal_negotiation import ChannelCapability  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("intent")
    parser.add_argument("--budget", type=Path, required=True)
    parser.add_argument("--requests", type=Path, required=True)
    parser.add_argument("--channels", type=Path)
    args = parser.parse_args()

    budget = ResourceBudget(**json.loads(args.budget.read_text(encoding="utf-8")))
    request_rows = json.loads(args.requests.read_text(encoding="utf-8"))
    requests = [
        ResourceRequest(
            operation_id=row["operation_id"],
            expected_value=row["expected_value"],
            expected_information_gain=row["expected_information_gain"],
            urgency=row["urgency"],
            risk=row["risk"],
            resources=ResourceBudget(**row["resources"]),
            reversible=row.get("reversible", True),
            requires_authorization=row.get("requires_authorization", False),
        )
        for row in request_rows
    ]

    channels = []
    if args.channels:
        packet = json.loads(args.channels.read_text(encoding="utf-8"))
        channels = [
            ChannelCapability(
                channel=row["channel"],
                available=bool(row["available"]),
                consent_scopes=tuple(row.get("consent_scopes", [])),
                attention=float(row["attention"]),
                reliability=float(row["reliability"]),
                cost=float(row["cost"]),
                max_priority=float(row.get("max_priority", 1.0)),
                preferred_rank=int(row.get("preferred_rank", 100)),
            )
            for row in packet["channels"]
        ]

    result = plan(
        args.intent,
        resources=budget,
        requests=requests,
        channels=channels,
    )
    print(json.dumps(result, indent=2, sort_keys=True))

    return {
        "REQUIRES_SPECIFICATION": 2,
        "AUTHORIZATION_REQUIRED": 0,
        "READY_FOR_VERIFICATION": 0,
    }.get(result["status"], 1)


if __name__ == "__main__":
    raise SystemExit(main())
