#!/usr/bin/env python3
"""Phone-first CLI wrapper for the EVEZ information frontier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# When invoked as "python mobile/evez_frontier.py", Python starts with the
# mobile directory on sys.path. Add the repository root explicitly so the
# research package resolves identically on Termux and CI.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from research.information_frontier import (  # noqa: E402
    KnowledgeItem,
    SourceCapability,
    build_frontier,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    packet = json.loads(args.packet.read_text(encoding="utf-8"))

    items = [KnowledgeItem(**row) for row in packet.get("items", [])]
    sources = [
        SourceCapability(
            source_id=row["source_id"],
            topics=tuple(row.get("topics", [])),
            accessible=bool(row.get("accessible", False)),
            freshness=float(row.get("freshness", 0.0)),
            estimated_cost=float(row.get("estimated_cost", 1.0)),
            independence_group=row.get("independence_group"),
        )
        for row in packet.get("sources", [])
    ]

    result = build_frontier(
        items,
        sources,
        now_tick=int(packet.get("now_tick", 0)),
        limit=int(packet.get("limit", 8)),
    )

    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
