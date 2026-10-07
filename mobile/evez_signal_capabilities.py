#!/usr/bin/env python3
"""Discover locally installed EVEZ signal adapters without inventing consent."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


DEFAULTS = {
    "text": (1.0, 0.99, 0.1, 0),
    "visual": (0.95, 0.90, 1.0, 1),
    "audio": (0.90, 0.85, 1.2, 2),
    "haptic": (0.80, 0.80, 0.5, 3),
    "wearable": (0.90, 0.70, 1.5, 4),
    "ambient": (0.50, 0.60, 0.8, 5),
    "sensor": (0.30, 0.50, 1.0, 6),
}

COMMANDS = {
    "text": None,
    "visual": "termux-notification",
    "audio": "termux-tts-speak",
    "haptic": "termux-vibrate",
    "wearable": None,
    "ambient": None,
    "sensor": None,
}


def discover(consent_scopes: tuple[str, ...]) -> dict:
    channels = []
    for channel, (attention, reliability, cost, rank) in DEFAULTS.items():
        command = COMMANDS[channel]
        available = True if channel == "text" else bool(command and shutil.which(command))
        channels.append(
            {
                "channel": channel,
                "available": available,
                "adapter": command,
                "consent_scopes": list(consent_scopes),
                "consent_detected": bool(consent_scopes),
                "attention": attention,
                "reliability": reliability,
                "cost": cost,
                "max_priority": 1.0,
                "preferred_rank": rank,
            }
        )

    return {
        "schema": "evez-signal-capabilities-v1",
        "discovery": "local_command_probe",
        "consent_scopes": list(consent_scopes),
        "channels": channels,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--consent-scope", action="append", default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = discover(tuple(sorted(set(args.consent_scope))))
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
