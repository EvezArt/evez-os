#!/usr/bin/env python3
"""Termux signal adapter.

Queues and optionally renders a signal through installed Termux:API commands.
No network access is implicit. No signal is delivered without explicit
--deliver, and unavailable modalities fail closed.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from research.signal_domain import SignalEnvelope, render_for_channel


def available(command: str) -> bool:
    return shutil.which(command) is not None


def deliver(rendered: dict) -> dict:
    channel = rendered["channel"]
    title = rendered["title"]
    payload = rendered["payload"]
    body = json.dumps(payload, sort_keys=True, ensure_ascii=False)

    if channel == "text":
        print(f"{title}: {body}")
        return {"delivered": True, "adapter": "stdout", "digest": rendered["digest"]}

    if channel == "visual":
        command = "termux-notification"
        if not available(command):
            return {"delivered": False, "reason": "termux-notification unavailable"}
        subprocess.run(
            [command, "--title", title, "--content", body],
            check=True,
        )
        return {"delivered": True, "adapter": command, "digest": rendered["digest"]}

    if channel == "audio":
        command = "termux-tts-speak"
        if not available(command):
            return {"delivered": False, "reason": "termux-tts-speak unavailable"}
        subprocess.run([command, f"{title}. {body}"], check=True)
        return {"delivered": True, "adapter": command, "digest": rendered["digest"]}

    if channel == "haptic":
        command = "termux-vibrate"
        if not available(command):
            return {"delivered": False, "reason": "termux-vibrate unavailable"}
        subprocess.run([command, "-d", "500"], check=True)
        return {"delivered": True, "adapter": command, "digest": rendered["digest"]}

    if channel == "wearable":
        command = "termux-notification"
        if not available(command):
            return {"delivered": False, "reason": "termux-notification unavailable"}
        subprocess.run(
            [command, "--title", title, "--content", body, "--priority", "high"],
            check=True,
        )
        return {"delivered": True, "adapter": command, "digest": rendered["digest"]}

    return {"delivered": False, "reason": f"no Termux adapter for {channel}"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--channel", required=True)
    parser.add_argument("--deliver", action="store_true")
    args = parser.parse_args()

    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    signal = SignalEnvelope(**packet)
    rendered = render_for_channel(signal, args.channel)

    if not args.deliver:
        print(json.dumps({
            "delivered": False,
            "dry_run": True,
            "rendered": rendered,
        }, indent=2, sort_keys=True))
        return 0

    result = deliver(rendered)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("delivered") else 1


if __name__ == "__main__":
    raise SystemExit(main())
