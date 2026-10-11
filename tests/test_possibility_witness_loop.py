"""Regression tests for the offline EVEZ possibility/witness contract."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import unittest

from evez_possibility_witness_loop import (
    authorize_handoff,
    can_retry,
    claim_satisfies_state,
    contradiction_record,
    evaluate_witness_receipt,
    ReplayGuard,
    seal_witness,
    validate_handoff,
    verify_artifact_digest,
    verify_sealed_witness,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_NOW = datetime(2029, 12, 31, 23, 59, tzinfo=timezone.utc)


class PossibilityWitnessLoopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.envelope = json.loads(
            (ROOT / "examples/evez-handoff-v1.example.json").read_text(encoding="utf-8")
        )
        cls.artifact = (ROOT / "examples/fixtures/possibility-witness-artifact.txt").read_bytes()
        cls.recipient = deepcopy(cls.envelope["recipient"])
        cls.capabilities = set(cls.envelope["requested_capabilities"])

    def test_example_handoff_is_valid_before_expiry(self) -> None:
        self.assertEqual(validate_handoff(self.envelope, now=FIXTURE_NOW), [])

    def test_example_artifact_hash_matches_real_fixture_bytes(self) -> None:
        expected = self.envelope["artifacts"][0]["sha256"]
        self.assertTrue(verify_artifact_digest(expected, self.artifact))

    def test_tampered_artifact_is_rejected(self) -> None:
        expected = self.envelope["artifacts"][0]["sha256"]
        self.assertFalse(verify_artifact_digest(expected, self.artifact + b"tampered"))

    def test_unknown_top_level_property_is_rejected(self) -> None:
        altered = deepcopy(self.envelope)
        altered["authority_override"] = True
        self.assertTrue(any("unknown top-level keys" in e for e in validate_handoff(altered, now=FIXTURE_NOW)))

    def test_expired_handoff_is_rejected(self) -> None:
        after_expiry = datetime(2030, 1, 1, 0, 16, tzinfo=timezone.utc)
        self.assertIn("handoff is expired", validate_handoff(self.envelope, now=after_expiry))

    def test_future_dated_handoff_is_rejected(self) -> None:
        future = deepcopy(self.envelope)
        future["created_at"] = "2030-01-01T00:10:00Z"
        self.assertIn("handoff is not yet valid", validate_handoff(future, now=FIXTURE_NOW))

    def test_non_object_authorization_input_fails_closed(self) -> None:
        decision = authorize_handoff(
            None, recipient=self.recipient, granted_capabilities=self.capabilities, now=FIXTURE_NOW,
        )
        self.assertEqual(decision["decision"], "DENY")
        self.assertIn("invalid_handoff", decision["reasons"])
        self.assertFalse(decision["execution_performed"])

    def test_malformed_capability_shape_fails_closed_without_exception(self) -> None:
        malformed = deepcopy(self.envelope)
        malformed["requested_capabilities"] = {"unexpected": "mapping"}
        decision = authorize_handoff(
            malformed, recipient=self.recipient, granted_capabilities=self.capabilities, now=FIXTURE_NOW,
        )
        self.assertEqual(decision["decision"], "DENY")
        self.assertIn("invalid_handoff", decision["reasons"])

    def test_non_string_grants_are_denied(self) -> None:
        decision = authorize_handoff(
            self.envelope, recipient=self.recipient, granted_capabilities=[None], now=FIXTURE_NOW,
        )
        self.assertEqual(decision["decision"], "DENY")
        self.assertIn("invalid_granted_capabilities", decision["reasons"])

    def test_non_iterable_grants_are_denied_without_exception(self) -> None:
        decision = authorize_handoff(
            self.envelope, recipient=self.recipient, granted_capabilities=5, now=FIXTURE_NOW,
        )
        self.assertEqual(decision["decision"], "DENY")
        self.assertIn("invalid_granted_capabilities", decision["reasons"])
        self.assertFalse(decision["execution_performed"])

    def test_wrong_recipient_is_denied(self) -> None:
        decision = authorize_handoff(
            self.envelope, recipient={"provider": "hermes", "agent_id": "different-agent"},
            granted_capabilities=self.capabilities, now=FIXTURE_NOW,
        )
        self.assertEqual(decision["decision"], "DENY")
        self.assertIn("recipient_mismatch", decision["reasons"])

    def test_missing_capability_is_denied(self) -> None:
        decision = authorize_handoff(
            self.envelope, recipient=self.recipient, granted_capabilities={"artifact.read"}, now=FIXTURE_NOW,
        )
        self.assertEqual(decision["decision"], "DENY")
        self.assertTrue(any(reason.startswith("missing_capabilities:") for reason in decision["reasons"]))

    def test_read_only_gate_blocks_writes(self) -> None:
        decision = authorize_handoff(
            self.envelope, recipient=self.recipient, granted_capabilities=self.capabilities,
            operation="write", read_only=True, now=FIXTURE_NOW,
        )
        self.assertEqual(decision["decision"], "DENY")
        self.assertIn("read_only_mode", decision["reasons"])
        self.assertFalse(decision["execution_performed"])

    def test_r3_write_requires_scoped_approval(self) -> None:
        elevated = deepcopy(self.envelope)
        elevated["risk_class"] = "R3"
        elevated["approval_required"] = True
        decision = authorize_handoff(
            elevated, recipient=self.recipient, granted_capabilities=self.capabilities,
            operation="write", read_only=False, approval_granted=False, now=FIXTURE_NOW,
        )
        self.assertEqual(decision["decision"], "DENY")
        self.assertIn("human_approval_missing", decision["reasons"])

    def test_r3_cannot_bypass_explicit_approval_flag(self) -> None:
        elevated = deepcopy(self.envelope)
        elevated["risk_class"] = "R3"
        elevated["approval_required"] = False
        decision = authorize_handoff(
            elevated, recipient=self.recipient, granted_capabilities=self.capabilities,
            operation="write", read_only=False, approval_granted=True, now=FIXTURE_NOW,
        )
        self.assertEqual(decision["decision"], "DENY")
        self.assertIn("risk_R3_approval_flag_missing", decision["reasons"])

    def test_approved_r3_operation_passes_policy_simulation_only(self) -> None:
        elevated = deepcopy(self.envelope)
        elevated["risk_class"] = "R3"
        elevated["approval_required"] = True
        decision = authorize_handoff(
            elevated, recipient=self.recipient, granted_capabilities=self.capabilities,
            operation="write", read_only=False, approval_granted=True, now=FIXTURE_NOW,
        )
        self.assertEqual(decision["decision"], "ALLOW")
        self.assertFalse(decision["execution_performed"])

    def test_r4_is_denied_even_when_approval_is_present(self) -> None:
        prohibited = deepcopy(self.envelope)
        prohibited["risk_class"] = "R4"
        prohibited["approval_required"] = True
        decision = authorize_handoff(
            prohibited, recipient=self.recipient, granted_capabilities=self.capabilities,
            operation="write", read_only=False, approval_granted=True, now=FIXTURE_NOW,
        )
        self.assertEqual(decision["decision"], "DENY")
        self.assertIn("risk_R4_denied", decision["reasons"])

    def test_duplicate_idempotency_key_is_rejected_without_reexecution(self) -> None:
        guard = ReplayGuard()
        first = guard.accept_once(self.envelope, now=FIXTURE_NOW)
        replay = guard.accept_once(self.envelope, now=FIXTURE_NOW)
        self.assertEqual(first["decision"], "ALLOW")
        self.assertEqual(replay["decision"], "DENY")
        self.assertEqual(replay["reason"], "replay_detected")
        self.assertFalse(replay["execution_performed"])

    def test_proposal_does_not_satisfy_verified_acceptance(self) -> None:
        self.assertFalse(claim_satisfies_state("PROPOSED", "VERIFIED"))
        self.assertFalse(claim_satisfies_state("INFERRED", "VERIFIED"))
        self.assertTrue(claim_satisfies_state("VERIFIED", "VERIFIED"))

    def test_missing_terminal_receipt_cannot_be_promoted(self) -> None:
        result = evaluate_witness_receipt(
            {"terminal": False, "result_status": "SUCCEEDED", "checks": {"schema": "PASS"}},
            required_checks=["schema"],
        )
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "missing_terminal_receipt")

    def test_failed_or_missing_required_check_blocks_promotion(self) -> None:
        result = evaluate_witness_receipt(
            {
                "terminal": True, "result_status": "SUCCEEDED",
                "checks": {"schema": "PASS", "policy": "FAIL"},
                "verifier": {"independent": True, "identity": "verifier-fixture"},
            },
            required_checks=["schema", "policy"],
        )
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["failed_or_missing_checks"], ["policy"])

    def test_no_independent_verifier_caps_result_at_partial(self) -> None:
        result = evaluate_witness_receipt(
            {"terminal": True, "result_status": "SUCCEEDED", "checks": {"schema": "PASS"}},
            required_checks=["schema"],
        )
        self.assertEqual(result["status"], "partially_verified")

    def test_valid_terminal_receipt_with_independent_verifier_passes(self) -> None:
        result = evaluate_witness_receipt(
            {
                "terminal": True, "result_status": "REPRODUCED",
                "checks": {"schema": "PASS", "policy": "PASS"},
                "verifier": {"independent": True, "identity": "verifier-fixture"},
            },
            required_checks=["schema", "policy"],
        )
        self.assertEqual(result["status"], "verified")

    def test_contradictory_observations_are_both_preserved(self) -> None:
        source_a = {"observation_id": "obs-a", "source_id": "sensor-a", "claim": "value=1"}
        source_b = {"observation_id": "obs-b", "source_id": "sensor-b", "claim": "value=2"}
        result = contradiction_record([source_a, source_b], resolution_test="Repeat calibrated measurement")
        self.assertEqual(result["classification"], "CONTRADICTED")
        self.assertEqual(result["observations"], [source_a, source_b])
        self.assertEqual(result["observation_count"], 2)

    def test_witness_digest_detects_mutation(self) -> None:
        sealed = seal_witness({"task_id": "fixture-task", "result_status": "SUCCEEDED", "checks": ["schema"]})
        self.assertTrue(verify_sealed_witness(sealed))
        sealed["result_status"] = "FAILED"
        self.assertFalse(verify_sealed_witness(sealed))

    def test_remediation_cycles_are_bounded(self) -> None:
        self.assertTrue(can_retry(0, max_cycles=3))
        self.assertTrue(can_retry(2, max_cycles=3))
        self.assertFalse(can_retry(3, max_cycles=3))
        self.assertFalse(can_retry(-1, max_cycles=3))


if __name__ == "__main__":
    unittest.main(verbosity=2)
