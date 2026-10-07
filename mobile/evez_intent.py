#!/usr/bin/env python3
"""Termux wrapper for deterministic intent optimization."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.intent_optimizer import optimize_intent  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intent", action="append", dest="intents")
    parser.add_argument("--file", type=Path)
    args = parser.parse_args()

    if not args.intents and args.file is None:
        parser.error("provide --intent at least once or --file")

    candidates = list(args.intents or [])
    if args.file is not None:
        payload = json.loads(args.file.read_text(encoding="utf-8"))
        if not isinstance(payload, list) or not all(isinstance(item, str) for item in payload):
            raise SystemExit("candidate file must contain a JSON string array")
        candidates.extend(payload)

    result = optimize_intent(candidates)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "OPTIMIZED_CANDIDATE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
