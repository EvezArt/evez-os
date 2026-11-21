import unittest

from research.confluence_discriminator import (
    ConfluenceConfig,
    Event,
    analyze,
)


class ConfluenceDiscriminatorTests(unittest.TestCase):
    def test_same_actor_burst_is_internal_not_candidate(self):
        base = 1_760_000_000
        events = [
            Event(base + i * 20, "EvezArt", f"deploy module {i}", "github", "repo")
            for i in range(4)
        ]
        out = analyze(events, ConfluenceConfig(permutations=50, random_seed=1))
        self.assertEqual(out["results"][0]["label"], "INTERNAL_OPERATOR_BURST")

    def test_bot_burst_is_automation(self):
        base = 1_760_000_000
        events = [
            Event(base + i * 10, "dependabot[bot]", f"bump package {i}", "github", "repo")
            for i in range(4)
        ]
        out = analyze(events, ConfluenceConfig(permutations=50, random_seed=2))
        self.assertEqual(out["results"][0]["label"], "AUTOMATION_BURST")

    def test_diverse_sources_without_enough_semantic_convergence_stays_unknown(self):
        base = 1_760_000_000
        events = [
            Event(base + i * 5, f"actor-{i}", text, f"source-{i%2}", f"repo-{i}")
            for i, text in enumerate([
                "alpha weather",
                "database migration",
                "music rendering",
                "payment check",
                "compiler cleanup",
            ])
        ]
        out = analyze(events, ConfluenceConfig(permutations=80, random_seed=3))
        self.assertEqual(out["results"][0]["label"], "UNKNOWN_INSUFFICIENT_EVIDENCE")

    def test_mapping_input_is_supported(self):
        out = analyze([
            {"ts": "2026-10-05T04:29:00Z", "actor": "A", "text": "same shape",
             "source": "x", "repo": "r"},
            {"ts": "2026-10-05T04:29:10Z", "actor": "A", "text": "same shape",
             "source": "x", "repo": "r"},
            {"ts": "2026-10-05T04:29:20Z", "actor": "A", "text": "same shape",
             "source": "x", "repo": "r"},
        ], ConfluenceConfig(permutations=20))
        self.assertEqual(out["labels"]["INTERNAL_OPERATOR_BURST"], 1)


if __name__ == "__main__":
    unittest.main()
