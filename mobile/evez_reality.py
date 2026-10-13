# SPDX-License-Identifier: MIT
#!/usr/bin/env python3
"""Termux interface for the persistent EVEZ reality substrate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.reality_substrate import (
    CausalEvent,
    DirectorCandidate,
    ProjectionSpec,
    WorldEntity,
    WorldSnapshot,
    choose_next_operation,
    compile_projection,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    project = sub.add_parser("project")
    project.add_argument("snapshot")
    project.add_argument("representation")
    project.add_argument("observer")

    choose = sub.add_parser("choose")
    choose.add_argument("candidates")

    args = parser.parse_args()

    if args.command == "project":
        snapshot = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
        spec = ProjectionSpec(
            projection_id=f"mobile:{snapshot['snapshot_id']}",
            representation=args.representation,
            observer_id=args.observer,
            snapshot_id=snapshot["snapshot_id"],
            parameters=snapshot.get("parameters", {}),
        )
        entities = tuple(WorldEntity(**row) for row in snapshot.get("entities", []))
        events = tuple(CausalEvent(**row) for row in snapshot.get("events", []))
        world = WorldSnapshot(
            snapshot_id=snapshot["snapshot_id"],
            timestamp=snapshot["timestamp"],
            parent_snapshot=snapshot.get("parent_snapshot"),
            entities=entities,
            events=events,
            branch=snapshot.get("branch", "main"),
        )
        print(json.dumps(compile_projection(world, spec).__dict__, indent=2, sort_keys=True))
        return 0

    if args.command == "choose":
        payload = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
        rows = [DirectorCandidate(**item) for item in payload]
        print(json.dumps(choose_next_operation(rows), indent=2, sort_keys=True))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
