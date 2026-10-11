import unittest
from research.spacetime_interval import SPEED_OF_LIGHT_M_S, classify_interval


class SpacetimeIntervalTests(unittest.TestCase):
    def test_timelike(self):
        result = classify_interval(1.0, 0.0)
        self.assertEqual(result["classification"], "TIMELIKE")
        self.assertGreater(result["interval_squared_m2"], 0)

    def test_spacelike(self):
        result = classify_interval(1e-9, 1.0)
        self.assertEqual(result["classification"], "SPACELIKE")
        self.assertLess(result["interval_squared_m2"], 0)
        self.assertTrue(result["coordinate_speed_exceeds_c"])
        self.assertIn("no signal transfer", result["scope"])

    def test_lightlike(self):
        result = classify_interval(1.0, SPEED_OF_LIGHT_M_S)
        self.assertEqual(result["classification"], "LIGHTLIKE_OR_WITHIN_TOLERANCE")
        self.assertAlmostEqual(result["interval_squared_m2"], 0.0, places=4)

    def test_coincident_event(self):
        self.assertEqual(classify_interval(0.0, 0.0)["classification"], "COINCIDENT_EVENT")

    def test_rejects_nonfinite_values(self):
        with self.assertRaises(ValueError):
            classify_interval(float("nan"), 1.0)

    def test_rejects_bad_tolerance(self):
        with self.assertRaises(ValueError):
            classify_interval(1.0, 1.0, relative_tolerance=-1.0)


if __name__ == "__main__":
    unittest.main()
