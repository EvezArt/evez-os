import unittest
from research.warp_bubble_profile import analyze_profile, radial_derivative, shape_value


class WarpBubbleProfileTests(unittest.TestCase):
    def test_shape_is_normalized_at_center(self):
        self.assertAlmostEqual(shape_value(0.0, 10.0, 1.0), 1.0, places=12)

    def test_profile_tends_toward_zero_far_outside(self):
        self.assertLess(shape_value(100.0, 10.0, 1.0), 1e-12)

    def test_radial_derivative_vanishes_at_center(self):
        self.assertAlmostEqual(radial_derivative(0.0, 10.0, 1.0), 0.0, places=12)

    def test_profile_diagnostics_include_hard_limits(self):
        report = analyze_profile(10.0, 1.0, 101)
        self.assertEqual(report["claim_classification"], "speculative")
        self.assertEqual(report["parameters"]["samples"], 101)
        self.assertTrue(report["not_computed"])
        self.assertIn("not evidence of superluminal travel", report["interpretation_limit"])
        self.assertEqual(len(report["profile"]), 101)

    def test_invalid_inputs_are_rejected(self):
        for radius, sigma in ((0, 1), (10, 0), (-1, 1), (float("nan"), 1)):
            with self.subTest(radius=radius, sigma=sigma):
                with self.assertRaises(ValueError):
                    analyze_profile(radius, sigma)


if __name__ == "__main__":
    unittest.main()
