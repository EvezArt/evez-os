#!/usr/bin/env python3
from __future__ import annotations

import hashlib

from epistemic_gate import audit


def h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def good_packet() -> dict:
    return {
        "schema_version": 1,
        "claims": [
            {
                "id": "c1",
                "text": "Observed synthetic reading.",
                "status": "OBSERVED",
                "confidence": 0.8,
                "evidence_ids": ["e1"],
                "observations": ["sensor-a"],
            },
            {
                "id": "c2",
                "text": "Identity remains unknown.",
                "status": "UNKNOWN",
                "truth": None,
                "confidence": 0.2,
                "evidence_ids": [],
                "observations": ["sensor-a"],
            },
        ],
        "evidence": [
            {
                "id": "e1",
                "source": "synthetic",
                "content": "reading-1",
                "sha256": h("reading-1"),
            }
        ],
        "contradictions": [],
    }


def test_clean_packet_reaches_g2() -> None:
    out = audit(good_packet())
    assert out["grade"] == "G2"
    assert out["admitted"] is True
    assert out["revelation_ready"] is True
    assert out["derived"]["truth_certificate"] is False


def test_evidence_tampering_is_rejected() -> None:
    packet = good_packet()
    packet["evidence"][0]["content"] = "tampered"
    out = audit(packet)
    assert out["grade"] == "G0"
    assert out["admitted"] is False


def test_ordering_does_not_change_semantics() -> None:
    packet = good_packet()
    out = audit(packet)
    control = next(x for x in out["controls"] if x["name"] == "ordering_invariance")
    assert control["passed"] is True


def test_unsupported_unknown_promotion_is_caught() -> None:
    packet = good_packet()
    out = audit(packet)
    control = next(
        x for x in out["controls"]
        if x["name"] == "unsupported_unknown_promotion_detection"
    )
    assert control["passed"] is True


def test_bad_certainty_never_reaches_gate() -> None:
    packet = good_packet()
    packet["claims"][0]["evidence_ids"] = []
    packet["claims"][0]["observations"] = []
    out = audit(packet)
    assert out["grade"] == "G0"
    assert out["admitted"] is False


if __name__ == "__main__":
    tests = [
        test_clean_packet_reaches_g2,
        test_evidence_tampering_is_rejected,
        test_ordering_does_not_change_semantics,
        test_unsupported_unknown_promotion_is_caught,
        test_bad_certainty_never_reaches_gate,
    ]
    for test in tests:
        test()
    print("epistemic gate tests: PASS")
