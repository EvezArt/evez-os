from research.signal_delivery import make_receipt, receipt_digest
from research.signal_domain import SignalEnvelope

signal = SignalEnvelope(
    signal_id="sig-9",
    timestamp="2026-10-07T18:40:00Z",
    channel="text",
    intent="ALERT",
    title="Test",
    payload={"x": 1},
    provenance={"source": "swarm"},
    consent_scope="operator-alerts",
)

r1 = make_receipt(
    signal,
    channel="audio",
    state="ACK",
    attempt=1,
    adapter="termux-tts-speak",
    delivered=True,
    timestamp="2026-10-07T18:40:01Z",
)
r2 = make_receipt(
    signal,
    channel="audio",
    state="ACK",
    attempt=1,
    adapter="termux-tts-speak",
    delivered=True,
    timestamp="2026-10-07T18:40:01Z",
)

assert r1 == r2
assert r1.signal_digest
assert len(receipt_digest(r1)) == 64
assert r1.state == "ACK"

print("signal delivery tests: PASS")
