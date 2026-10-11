import tempfile
import unittest
from pathlib import Path

from integrations.spacetime_telegram_bridge import handle_command, parse_allowed_user_ids
from research.spacetime_breakthrough_lab import verify_ledger


class SpacetimeTelegramBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ledger = Path(self.temp.name) / "telegram.jsonl"
        self.allowed = {12345}

    def call(self, text, sender=12345, chat_type="private", update_id=1):
        return handle_command(text, sender_id=sender, chat_type=chat_type, allowed_ids=self.allowed, ledger_path=self.ledger, update_id=update_id)

    def test_rejects_unallowlisted_user_without_response(self):
        self.assertIsNone(self.call("/status", sender=999, update_id=5))

    def test_rejects_group_messages(self):
        self.assertIsNone(self.call("/proposal t | h | m", chat_type="group", update_id=5))

    def test_requires_numeric_allowlist(self):
        self.assertEqual(parse_allowed_user_ids("12, 34"), {12, 34})
        with self.assertRaises(ValueError):
            parse_allowed_user_ids("12,secret")
        with self.assertRaises(ValueError):
            parse_allowed_user_ids("")

    def test_proposal_registers_speculative_hypothesis(self):
        reply = self.call("/proposal Metric screen | A metric ansatz satisfies constraints | symbolic-screen", update_id=9)
        self.assertIn("Registered PROPOSED", reply)
        self.assertTrue(verify_ledger(self.ledger)["ok"])

    def test_duplicate_update_is_not_recorded_twice(self):
        self.call("/proposal Metric screen | A metric ansatz satisfies constraints | symbolic-screen", update_id=9)
        reply = self.call("/proposal Metric screen | A metric ansatz satisfies constraints | symbolic-screen", update_id=9)
        self.assertIn("already recorded", reply)
        self.assertEqual(verify_ledger(self.ledger)["events"], 1)

    def test_unknown_commands_do_not_run_any_tools(self):
        self.assertEqual(self.call("/shell rm -rf /", update_id=4), "Unknown command. Use /help.")

    def test_observation_requires_registered_experiment(self):
        reply = self.call("/observation router | ruview_csi | phase | 0.3 | radians | calibration-1 | room test", update_id=10)
        self.assertIn("register an experiment before adding observations", reply)
        self.assertFalse(self.ledger.exists())

    def test_observation_after_proposal(self):
        self.call("/proposal Metric screen | A metric ansatz satisfies constraints | symbolic-screen", update_id=9)
        reply = self.call("/observation simulator | simulation | residual | 0.0 | dimensionless | build-1 | synthetic", update_id=10)
        self.assertIn("Observation recorded", reply)
        self.assertEqual(verify_ledger(self.ledger)["events"], 2)


if __name__ == "__main__":
    unittest.main()
