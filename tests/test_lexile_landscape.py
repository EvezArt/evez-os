import unittest
from mobile.evez_lexile_landscape import amplify

class LexileLandscapeTests(unittest.TestCase):
    def test_deterministic(self):
        a = amplify("metamemetic permaloot emotion", rounds=2)
        b = amplify("metamemetic permaloot emotion", rounds=2)
        self.assertEqual(a["lexile_landscape_sha256"], b["lexile_landscape_sha256"])

    def test_observable_only(self):
        result = amplify("mental lexile landscaping")
        self.assertEqual(result["mode"], "OBSERVABLE_LEXILE_AMPLIFICATION")
        self.assertIn("LANGUAGE != MIND_ACCESS", result["invariants"])

    def test_proposed_terms(self):
        result = amplify("permaloot", rounds=1, max_nodes=40)
        self.assertTrue(result["nodes"])
        self.assertTrue(all(node["status"] == "PROPOSED" for node in result["nodes"]))

if __name__ == "__main__":
    unittest.main()
