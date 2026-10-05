import unittest

from mobile.evez_response_loop import run


class ResponseLoopTests(unittest.TestCase):
    def test_extracts_visible_missing_data(self):
        context = {
            "claims": [{
                "claim_id": "c1",
                "statement": "The architecture is proven.",
                "evidence_state": "UNKNOWN",
            }],
            "assets": [{
                "asset_id": "a1",
                "name": "demo",
                "provenance": [],
            }],
        }
        result = run(context, "A response discussing the architecture.")
        directive = result["directive"]
        self.assertTrue(directive["required_data"])
        self.assertIn("HIDDEN_PROMPT_NOT_EXTRACTED", result["invariants"])

    def test_deterministic_for_same_inputs(self):
        context = {"constraints": {"mode": "proposal"}}
        a = run(context, "same response")
        b = run(context, "same response")
        self.assertEqual(a["response_loop_sha256"], b["response_loop_sha256"])

    def test_compression_does_not_claim_to_bypass_limits(self):
        result = run({}, "")
        self.assertEqual(result["directive"]["token_strategy"].split(":", 1)[0], "compress-first")
        self.assertIn("INTERNAL_RESOURCE_NOT_BYPASSED", result["invariants"])


if __name__ == "__main__":
    unittest.main()
