import unittest

from research.counterfactual_threat_map import analyze


class CounterfactualThreatMapTests(unittest.TestCase):
    def test_single_actor_burst_is_not_coordination(self):
        rows = [
            {
                "ts": f"2026-10-05T00:0{i}:00Z",
                "actor": "A",
                "source": "github",
                "text": f"generated job {i}",
            }
            for i in range(5)
        ]
        out = analyze(rows, bucket_seconds=600, permutations=100)
        self.assertEqual(out["state"], "ANOMALY_NOT_COORDINATION_EVIDENCE")
        self.assertFalse(out["derived"]["coordination_supported"])

    def test_two_actor_two_source_burst_can_be_measured(self):
        rows = [
            {"ts": "2026-10-05T00:00:01Z", "actor": "A", "source": "x", "text": "please review this exact template now"},
            {"ts": "2026-10-05T00:00:02Z", "actor": "B", "source": "y", "text": "please review this exact template now"},
            {"ts": "2026-10-05T00:00:03Z", "actor": "A", "source": "x", "text": "please review this exact template now"},
            {"ts": "2026-10-05T00:00:04Z", "actor": "B", "source": "y", "text": "please review this exact template now"},
        ]
        out = analyze(rows, bucket_seconds=600, permutations=300)
        self.assertEqual(out["observed"]["unique_actors"], 2)
        self.assertEqual(out["observed"]["unique_sources"], 2)

    def test_missing_source_prevents_coordination_claim(self):
        rows = [
            {"ts": "2026-10-05T00:00:01Z", "actor": "A", "source": "only", "text": "same words one"},
            {"ts": "2026-10-05T00:00:02Z", "actor": "B", "source": "only", "text": "same words one"},
        ]
        out = analyze(rows, permutations=100)
        self.assertFalse(out["derived"]["independent_axes"])
        self.assertNotEqual(out["state"], "SUPPORTED_COORDINATION_SIGNAL")


if __name__ == "__main__":
    unittest.main()
