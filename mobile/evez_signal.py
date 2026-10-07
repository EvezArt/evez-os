#!/usr/bin/env python3
"""Termux signal adapter with capability negotiation and fail-closed fallback."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from research.signal_delivery import make_receipt, receipt_digest  # noqa: E402
from research.signal_domain import SignalEnvelope, render_for_channel  # noqa: E402
from research.signal_negotiation import (  # noqa: E402
    ChannelCapability,
    NegotiationRequest,
    negotiate,
)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def available(command: str) -> bool:
    return shutil.which(command) is not None


def capability_from_row(row: dict) -> ChannelCapability:
    return ChannelCapability(
        channel=row["channel"],
        available=bool(row["available"]),
        consent_scopes=tuple(row.get("consent_scopes", [])),
        attention=float(row["attention"]),
        reliability=float(row["reliability"]),
        cost=float(row["cost"]),
        max_priority=float(row.get("max_priority", 1.0)),
        preferred_rank=int(row.get("preferred_rank", 100)),
    )


def load_capabilities(path: Path) -> list[ChannelCapability]:
    packet = json.loads(path.read_text(encoding="utf-8"))
    if packet.get("schema") != "evez-signal-capabilities-v1":
        raise ValueError("unsupported capability manifest schema")
    return [capability_from_row(row) for row in packet.get("channels", [])]


def deliver(rendered: dict) -> dict:
    channel = rendered["channel"]
    title = rendered["title"]
    payload = rendered["payload"]
    body = json.dumps(payload, sort_keys=True, ensure_ascii=False)

    try:
        if channel == "text":
            print(f"{title}: {body}")
            return {"delivered": True, "adapter": "stdout", "detail": "stdout rendering"}

        if channel == "visual":
            command = "termux-notification"
            if not available(command):
                return {"delivered": False, "adapter": command, "detail": "adapter unavailable"}
            subprocess.run([command, "--title", title, "--content", body], check=True)
            return {"delivered": True, "adapter": command, "detail": "notification posted"}

        if channel == "audio":
            command = "termux-tts-speak"
            if not available(command):
                return {"delivered": False, "adapter": command, "detail": "adapter unavailable"}
            subprocess.run([command, f"{title}. {body}"], check=True)
            return {"delivered": True, "adapter": command, "detail": "speech requested"}

        if channel == "haptic":
            command = "termux-vibrate"
            if not available(command):
                return {"delivered": False, "adapter": command, "detail": "adapter unavailable"}
            subprocess.run([command, "-d", "500"], check=True)
            return {"delivered": True, "adapter": command, "detail": "vibration requested"}

        if channel == "wearable":
            command = "termux-notification"
            if not available(command):
                return {"delivered": False, "adapter": command, "detail": "wearable notification unavailable"}
            subprocess.run(
                [command, "--title", title, "--content", body, "--priority", "high"],
                check=True,
            )
            return {"delivered": True, "adapter": command, "detail": "wearable-compatible notification requested"}

        return {"delivered": False, "adapter": channel, "detail": "no adapter registered"}
    except (OSError, subprocess.CalledProcessError) as exc:
        return {
            "delivered": False,
            "adapter": channel,
            "detail": f"adapter execution failed: {type(exc).__name__}",
        }


def receipt_for(
    signal: SignalEnvelope,
    *,
    channel: str,
    state: str,
    attempt: int,
    adapter: str,
    delivered: bool,
    detail: str,
):
    receipt = make_receipt(
        signal,
        channel=channel,
        state=state,
        attempt=attempt,
        adapter=adapter,
        delivered=delivered,
        timestamp=now(),
        detail=detail,
    )
    return {
        "receipt": receipt.__dict__,
        "receipt_sha256": receipt_digest(receipt),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--channel")
    parser.add_argument("--capabilities", type=Path)
    parser.add_argument("--auto", action="store_true")
    parser.add_argument("--deliver", action="store_true")
    args = parser.parse_args()

    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    signal = SignalEnvelope(**packet)

    plan = None
    channels: list[str]

    if args.auto:
        if not args.capabilities:
            parser.error("--auto requires --capabilities")
        capabilities = load_capabilities(args.capabilities)
        plan = negotiate(
            NegotiationRequest(
                signal_id=signal.signal_id,
                intent=signal.intent,
                priority=signal.priority,
                consent_scope=signal.consent_scope,
                max_channels=3,
                require_redundancy=signal.intent == "CRITICAL" or signal.priority >= 0.9,
            ),
            capabilities,
        )
        if plan["status"] == "NO_ELIGIBLE_CHANNEL":
            print(json.dumps({"delivered": False, "plan": plan}, indent=2, sort_keys=True))
            return 2

        preferred = [row["channel"] for row in plan["selected_channels"]]
        if args.deliver:
            channels = list(dict.fromkeys(preferred + plan["fallback_order"]))
        else:
            channels = preferred
    elif args.channel:
        channels = [args.channel]
    else:
        parser.error("provide --channel or --auto")

    output = {"signal_id": signal.signal_id, "plan": plan, "attempts": []}

    for attempt, channel in enumerate(channels, 1):
        rendered = render_for_channel(signal, channel)
        if not args.deliver:
            output["attempts"].append(
                {
                    "rendered": rendered,
                    "state": "RENDER",
                    "delivered": False,
                    "dry_run": True,
                }
            )
            continue

        outcome = deliver(rendered)
        state = "ACK" if outcome["delivered"] else "FALLBACK"
        receipt = receipt_for(
            signal,
            channel=channel,
            state=state,
            attempt=attempt,
            adapter=outcome["adapter"],
            delivered=outcome["delivered"],
            detail=outcome["detail"],
        )
        output["attempts"].append(
            {
                "rendered": rendered,
                "outcome": outcome,
                **receipt,
            }
        )

        if outcome["delivered"]:
            break

    output["delivered"] = any(
        attempt.get("outcome", {}).get("delivered", False)
        for attempt in output["attempts"]
    )
    output["state"] = "ACK" if output["delivered"] else ("RENDER" if not args.deliver else "FAILED")
    output["dry_run"] = not args.deliver
    print(json.dumps(output, indent=2, sort_keys=True))

    if args.deliver and not output["delivered"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
