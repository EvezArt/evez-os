#!/usr/bin/env python3
"""Termux wrapper for strict intent/spec precision checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.precision_contract import compile_from_intent, validate_spec  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--intent")
    group.add_argument("--spec", type=Path)
    args = parser.parse_args()

    if args.intent is not None:
        result = compile_from_intent(args.intent)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "PRECISE_ENOUGH_FOR_DECOMPOSITION" else 2

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    result = validate_spec(spec)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
