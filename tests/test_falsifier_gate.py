"""
tests/test_falsifier_gate.py
Verification tests for Constitutional Rule #2 guard.
Resolves: evez-os#3 acceptance criteria.
Run: pytest tests/test_falsifier_gate.py -v
"""

import pytest
from evez_tasks_worker_patch import assert_falsifier, ConstitutionalViolation


def test_rejects_null_falsifier():
    with pytest.raises(ConstitutionalViolation):
        assert_falsifier({"kind": "fire.event", "falsifier": None})


def test_rejects_empty_falsifier():
    with pytest.raises(ConstitutionalViolation):
        assert_falsifier({"kind": "fire.event", "falsifier": ""})


def test_rejects_whitespace_falsifier():
    with pytest.raises(ConstitutionalViolation):
        assert_falsifier({"kind": "fire.event", "falsifier": "   "})


def test_rejects_missing_falsifier():
    with pytest.raises(ConstitutionalViolation):
        assert_falsifier({"kind": "fire.event", "payload": "data"})


def test_accepts_valid_falsifier():
    assert_falsifier({"kind": "fire.event", "falsifier": "tx_abc123"})


def test_accepts_falsifier_tx_field():
    assert_falsifier({"kind": "fire.event", "falsifier_tx": "tx_def456"})


def test_accepts_tx_id_field():
    assert_falsifier({"kind": "fire.event", "tx_id": "0xdeadbeef"})


def test_accepts_proof_field():
    assert_falsifier({"kind": "fire.event", "proof": "sha256:abc"})


def test_error_message_includes_kind():
    try:
        assert_falsifier({"kind": "gossip.claim"})
    except ConstitutionalViolation as e:
        assert "gossip.claim" in str(e)


def test_error_message_includes_rule_number():
    try:
        assert_falsifier({})
    except ConstitutionalViolation as e:
        assert "Rule #2" in str(e)
