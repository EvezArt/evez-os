#!/usr/bin/env python3
"""Consent-bounded multimodal signal domain for reaching a human operator.

This module defines transport-neutral signal packets. It does not claim access
to hidden or extraordinary sensory channels. A channel is usable only when an
explicit adapter and consent policy say it is available.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any

CHANNELS = (
    "text",
    "visual",
    "audio",
    "haptic",
    "wearable",
    "ambient",
    "sensor",
)

INTENTS = ("INFO", "ALERT", "REQUEST", "CRITICAL")

@dataclass(frozen=True)
class SignalEnvelope:
    signal_id: str
    timestamp: str
    channel: str
    intent: str
    title: str
    payload: dict[str, Any]
    provenance: dict[str, Any]
    consent_scope: str
    ttl_seconds: int = 300
    priority: float = 0.5

    def validate(self) -> None:
        if self.channel not in CHANNELS:
            raise ValueError("unsupported signal channel")
        if self.intent not in INTENTS:
            raise ValueError("unsupported signal intent")
        if not self.signal_id or not self.timestamp:
            raise ValueError("signal identity and timestamp are required")
        if self.ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        if not 0.0 <= self.priority <= 1.0:
            raise ValueError("priority must be within [0,1]")
        if not self.consent_scope:
            raise ValueError("consent_scope is required")

def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def signal_digest(signal: SignalEnvelope) -> str:
    signal.validate()
    return hashlib.sha256(canonical(asdict(signal))).hexdigest()

def render_for_channel(signal: SignalEnvelope, channel: str) -> dict[str, Any]:
    """Produce an adapter-neutral rendering request.

    Rendering changes representation, never provenance or epistemic state.
    """
    signal.validate()
    if channel not in CHANNELS:
        raise ValueError("unsupported signal channel")

    base = {
        "signal_id": signal.signal_id,
        "digest": signal_digest(signal),
        "channel": channel,
        "intent": signal.intent,
        "title": signal.title,
        "payload": signal.payload,
        "provenance": signal.provenance,
        "consent_scope": signal.consent_scope,
        "ttl_seconds": signal.ttl_seconds,
        "priority": signal.priority,
    }

    if channel == "visual":
        base["format"] = "structured_visual"
    elif channel == "audio":
        base["format"] = "speech_or_tone"
    elif channel == "haptic":
        base["format"] = "pattern"
    elif channel == "wearable":
        base["format"] = "device_notification"
    elif channel == "ambient":
        base["format"] = "local_ambient_cue"
    elif channel == "sensor":
        base["format"] = "sensor_feedback"
    else:
        base["format"] = "text"

    return base
