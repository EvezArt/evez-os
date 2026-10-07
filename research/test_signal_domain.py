from research.signal_domain import SignalEnvelope, render_for_channel, signal_digest

signal = SignalEnvelope(
    signal_id="sig-001",
    timestamp="2026-10-07T18:30:00Z",
    channel="text",
    intent="ALERT",
    title="Evidence frontier update",
    payload={"state": "UNKNOWN", "next_action": "VERIFY"},
    provenance={"source": "evez-swarm", "evidence_digest": "abc"},
    consent_scope="operator-alerts",
    ttl_seconds=60,
    priority=0.8,
)

digest_a = signal_digest(signal)
digest_b = signal_digest(signal)
assert digest_a == digest_b
assert len(digest_a) == 64

visual = render_for_channel(signal, "visual")
audio = render_for_channel(signal, "audio")
haptic = render_for_channel(signal, "haptic")

assert visual["digest"] == audio["digest"] == haptic["digest"] == digest_a
assert visual["format"] == "structured_visual"
assert audio["format"] == "speech_or_tone"
assert haptic["format"] == "pattern"

try:
    render_for_channel(signal, "telepathy")
except ValueError:
    pass
else:
    raise AssertionError("unsupported hidden channel must fail closed")

try:
    SignalEnvelope(
        signal_id="bad",
        timestamp="2026-10-07T18:30:00Z",
        channel="audio",
        intent="ALERT",
        title="x",
        payload={},
        provenance={},
        consent_scope="",
    ).validate()
except ValueError:
    pass
else:
    raise AssertionError("missing consent scope must fail closed")

print("signal domain tests: PASS")
