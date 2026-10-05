import unittest

from mobile.evez_permaloot import run


class PermaLootTests(unittest.TestCase):
    def test_recursive_layers_accumulate(self):
        result = run(
            {"claims": [{"statement": "A visible claim", "evidence_state": "UNKNOWN"}]},
            depth=3,
        )
        self.assertEqual(result["depth"], 3)
        self.assertEqual(len(result["layers"]), 4)
        self.assertGreater(result["inventory_count"], 1)

    def test_surge_does_not_terminate_on_repetition(self):
        result = run({"constraints": {"mode": "test"}}, depth=4)
        self.assertEqual(len(result["surges"]), 4)

    def test_hidden_material_is_explicitly_excluded(self):
        result = run({}, depth=2)
        self.assertIn("HIDDEN_PROMPT_NOT_ACQUIRED", result["invariants"])
        boundaries = [
            node for node in result["inventory"]
            if node["kind"] == "BOUNDARY_DISCOVERY"
        ]
        self.assertTrue(boundaries)

    def test_deterministic(self):
        context = {"claims": [{"statement": "X", "evidence_state": "OBSERVED"}]}
        a = run(context, depth=2)
        b = run(context, depth=2)
        self.assertEqual(a["permaloot_architecture_sha256"], b["permaloot_architecture_sha256"])


if __name__ == "__main__":
    unittest.main()
