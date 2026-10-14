import unittest
from integrations.ruview_sensing_bridge import extract_observations, validate_ws_url


class RuViewSensingBridgeTests(unittest.TestCase):
    def test_extracts_only_allowlisted_scalar_features(self):
        frame = {
            "source": "live",
            "timestamp": 1780000000000,
            "features": {"mean_rssi": -43.5, "variance": 0.22, "motion_band_power": 0.13, "secret": "omit"},
            "nodes": [{"node_id": "private-device", "rssi_dbm": -42}],
            "classification": {"presence": True, "person_count": 3},
            "vital_signs": {"breathing_bpm": 13, "hr_proxy_bpm": 80}
        }
        results = extract_observations(frame, calibration_id="room-baseline-v1")
        self.assertEqual([r["quantity"] for r in results], ["features.mean_rssi", "features.variance", "features.motion_band_power"])
        self.assertEqual(results[0]["value"], -43.5)
        self.assertEqual(results[0]["unit"], "dBm")
        joined = repr(results).lower()
        self.assertNotIn("private-device", joined)
        self.assertNotIn("person_count", joined)
        self.assertNotIn("breathing_bpm", joined)
        self.assertNotIn("secret", joined)
        self.assertEqual(results[0]["source"], "ruview:live")

    def test_refuses_missing_calibration_id(self):
        with self.assertRaises(ValueError):
            extract_observations({"features": {"mean_rssi": -45}}, calibration_id="")

    def test_ignores_malformed_or_non_numeric_values(self):
        result = extract_observations({"features": {"mean_rssi": float("nan"), "variance": True, "motion_band_power": "0.2"}}, calibration_id="cal-v1")
        self.assertEqual(result, [])

    def test_ignores_frames_without_features(self):
        self.assertEqual(extract_observations({"vital_signs": {"breathing_bpm": 12}}, calibration_id="cal-v1"), [])

    def test_allows_local_ws(self):
        self.assertEqual(validate_ws_url("ws://127.0.0.1:3001/ws/sensing", token_present=False), "ws://127.0.0.1:3001/ws/sensing")

    def test_rejects_remote_unencrypted_ws(self):
        with self.assertRaises(ValueError):
            validate_ws_url("ws://192.0.2.10:3001/ws/sensing", token_present=False)

    def test_requires_token_for_tailnet_wss(self):
        with self.assertRaises(ValueError):
            validate_ws_url("wss://ruview.tailnet.ts.net/ws/sensing", token_present=False)
        self.assertEqual(validate_ws_url("wss://ruview.tailnet.ts.net/ws/sensing", token_present=True),
                         "wss://ruview.tailnet.ts.net/ws/sensing")


if __name__ == "__main__":
    unittest.main()
