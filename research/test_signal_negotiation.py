from research.signal_negotiation import (
    ChannelCapability,
    NegotiationRequest,
    negotiate,
)

caps = [
    ChannelCapability("visual", True, ("operator-alerts",), 0.95, 0.90, 1.0, preferred_rank=1),
    ChannelCapability("audio", True, ("operator-alerts",), 0.90, 0.85, 1.2, preferred_rank=2),
    ChannelCapability("haptic", True, ("operator-alerts",), 0.80, 0.80, 0.5, preferred_rank=3),
    ChannelCapability("text", True, ("quiet-info",), 0.70, 0.99, 0.2, preferred_rank=0),
    ChannelCapability("wearable", False, ("operator-alerts",), 1.0, 1.0, 0.1, preferred_rank=0),
]

request = NegotiationRequest(
    signal_id="sig-1",
    intent="CRITICAL",
    priority=0.95,
    consent_scope="operator-alerts",
    max_channels=3,
    require_redundancy=True,
)

a = negotiate(request, caps)
b = negotiate(request, caps)

assert a == b
assert a["schema"] == "evez-indelumvealoquivolution-v1"
assert a["status"] == "READY"
assert len(a["selected_channels"]) == 2
assert set(a["fallback_order"]) == {"visual", "audio", "haptic"}
assert "text" not in a["fallback_order"]
assert "wearable" not in a["fallback_order"]
assert len(a["plan_sha256"]) == 64

blocked = negotiate(
    NegotiationRequest(
        signal_id="sig-2",
        intent="INFO",
        priority=0.3,
        consent_scope="never-granted",
    ),
    caps,
)
assert blocked["status"] == "NO_ELIGIBLE_CHANNEL"

print("signal negotiation tests: PASS")
