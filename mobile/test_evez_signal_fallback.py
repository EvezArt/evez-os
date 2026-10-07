#!/usr/bin/env python3
"""Adversarial tests for multimodal delivery fallback."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
module_path = root / "mobile" / "evez_signal.py"

spec = importlib.util.spec_from_file_location("evez_signal", module_path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

from research.signal_domain import SignalEnvelope, render_for_channel
from research.signal_negotiation import (
    ChannelCapability,
    NegotiationRequest,
    negotiate,
)

signal = SignalEnvelope(
    signal_id="fallback-1",
    timestamp="2026-10-07T18:50:00Z",
    channel="text",
    intent="CRITICAL",
    title="fallback",
    payload={"state": "UNKNOWN"},
    provenance={"source": "test"},
    consent_scope="operator-alerts",
    priority=0.99,
)

caps = [
    ChannelCapability("audio", True, ("operator-alerts",), 0.9, 0.9, 1.0, preferred_rank=1),
    ChannelCapability("haptic", True, ("operator-alerts",), 0.8, 0.8, 0.5, preferred_rank=2),
    ChannelCapability("visual", True, ("operator-alerts",), 0.95, 0.95, 1.0, preferred_rank=3),
]

plan = negotiate(
    NegotiationRequest(
        signal_id=signal.signal_id,
        intent=signal.intent,
        priority=signal.priority,
        consent_scope=signal.consent_scope,
        require_redundancy=True,
    ),
    caps,
)

assert plan["status"] == "READY"
assert len(plan["fallback_order"]) == 3

original_available = module.available
module.available = lambda _command: False

try:
    seen = []
    for channel in plan["fallback_order"]:
        rendered = render_for_channel(signal, channel)
        outcome = module.deliver(rendered)
        seen.append(outcome)
        assert outcome["delivered"] is False

    assert len(seen) == 3
    assert all(item["delivered"] is False for item in seen)
finally:
    module.available = original_available

print("signal fallback adversarial tests: PASS")
