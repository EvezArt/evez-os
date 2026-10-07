#!/usr/bin/env python3
"""Delivery state and receipt primitives for multimodal EVEZ signals."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any

from research.signal_domain import SignalEnvelope, signal_digest
from research.signal_negotiation import SIGNAL_STATES


@dataclass(frozen=True)
class DeliveryReceipt:
    signal_id: str
    signal_digest: str
    channel: str
    state: str
    attempt: int
    adapter: str
    delivered: bool
    timestamp: str
    detail: str = ""

    def validate(self) -> None:
        if self.state not in SIGNAL_STATES:
            raise ValueError("invalid delivery state")
        if self.attempt <= 0:
            raise ValueError("attempt must be positive")
        if not self.signal_id or not self.signal_digest or not self.timestamp:
            raise ValueError("receipt identity is incomplete")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def receipt_digest(receipt: DeliveryReceipt) -> str:
    receipt.validate()
    return hashlib.sha256(canonical(asdict(receipt))).hexdigest()


def make_receipt(
    signal: SignalEnvelope,
    *,
    channel: str,
    state: str,
    attempt: int,
    adapter: str,
    delivered: bool,
    timestamp: str,
    detail: str = "",
) -> DeliveryReceipt:
    return DeliveryReceipt(
        signal_id=signal.signal_id,
        signal_digest=signal_digest(signal),
        channel=channel,
        state=state,
        attempt=attempt,
        adapter=adapter,
        delivered=delivered,
        timestamp=timestamp,
        detail=detail,
    )
