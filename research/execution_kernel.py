#!/usr/bin/env python3
"""Bounded EVEZ outcome kernel: compile, allocate, verify, signal."""

from __future__ import annotations

from typing import Any, Iterable

from research.materium import ResourceBudget, ResourceRequest, allocate
from research.outcome_engine import compile_outcome
from research.signal_domain import SignalEnvelope, signal_digest
from research.signal_negotiation import ChannelCapability, NegotiationRequest, negotiate


def plan(
    intent: str,
    *,
    resources: ResourceBudget,
    requests: Iterable[ResourceRequest],
    channels: Iterable[ChannelCapability] = (),
) -> dict[str, Any]:
    outcome = compile_outcome(intent)
    authorization_available = False
    allocation = allocate(
        resources,
        requests,
        authorization_available=authorization_available,
    )

    signal = SignalEnvelope(
        signal_id="outcome:" + outcome["outcome"]["outcome_id"],
        timestamp="1970-01-01T00:00:00Z",
        channel="text",
        intent="INFO" if outcome["outcome"]["action_class"] != "CONSEQUENTIAL" else "CRITICAL",
        title="Outcome plan",
        payload=outcome,
        provenance={"source": "execution_kernel", "state": "MODEL_ONLY"},
        consent_scope="operator-info",
        priority=0.95 if outcome["outcome"]["requires_authorization"] else 0.5,
    )

    channel_plan = negotiate(
        NegotiationRequest(
            signal_id=signal.signal_id,
            intent=signal.intent,
            priority=signal.priority,
            consent_scope=signal.consent_scope,
            require_redundancy=signal.intent == "CRITICAL",
        ),
        channels,
    )

    required = outcome["outcome"]["requires_authorization"]
    return {
        "schema": "evez-execution-kernel-v1",
        "outcome": outcome,
        "allocation": allocation,
        "signal": {
            "signal_id": signal.signal_id,
            "signal_digest": signal_digest(signal),
        },
        "channel_plan": channel_plan,
        "authorization": {
            "required": required,
            "available": authorization_available,
            "consequential_execution_blocked": required and not authorization_available,
        },
        "status": "AUTHORIZATION_REQUIRED" if required else "READY_FOR_VERIFICATION",
    }
