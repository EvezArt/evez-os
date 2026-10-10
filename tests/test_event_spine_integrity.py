import hashlib
import importlib.util
import json
import math
from pathlib import Path
import unittest
import rfc8785

MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "services" / "event_spine.py"
spec = importlib.util.spec_from_file_location("evez_event_spine_integrity_test", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
EventSpine = module.EventSpine


def legacy_v1_event(seq, prev_hash, domain, action, data, timestamp):
    hash_input = f"{seq}:{prev_hash}:{domain}:{action}:{json.dumps(data, sort_keys=True, default=str)}"
    return {
        "seq": seq,
        "domain": domain,
        "action": action,
        "data": data,
        "timestamp": timestamp,
        "prev_hash": prev_hash,
        "hash": hashlib.sha256(hash_input.encode()).hexdigest(),
    }


class EventSpineIntegrityTests(unittest.TestCase):
    def test_new_v2_events_cover_content_and_timestamp(self):
        spine = EventSpine()
        event = spine.append("epie", "OBSERVED_FACT", {"claim": "reported"}, timestamp=0.0)
        self.assertEqual(event["hash_version"], 2)
        payload = {key: value for key, value in event.items() if key != "hash"}
        expected_hash = hashlib.sha256(rfc8785.dumps(payload)).hexdigest()
        self.assertEqual(event["hash"], expected_hash)
        self.assertTrue(spine.verify()["valid"])
        spine._events[0]["data"]["claim"] = "changed"
        result = spine.verify()
        self.assertFalse(result["valid"])
        self.assertIn("event content hash mismatch", [entry["error"] for entry in result["errors"]])

    def test_timestamp_mutation_is_detected_for_v2(self):
        spine = EventSpine()
        spine.append("epie", "EVIDENCE_COMMIT", {"source_hash": "abc"}, timestamp=100.0)
        spine._events[0]["timestamp"] = 101.0
        self.assertFalse(spine.verify()["valid"])

    def test_legacy_v1_verifies_with_explicit_timestamp_warning(self):
        spine = EventSpine()
        spine._events = [legacy_v1_event(0, "0" * 64, "legacy", "event", {"x": 1}, 1.0)]
        spine.index = {"legacy": [0]}
        result = spine.verify()
        self.assertTrue(result["valid"])
        self.assertIn("legacy v1 hash does not cover timestamp or extra fields",
                      [entry["warning"] for entry in result["warnings"]])
        # Document, rather than conceal, the historical v1 limitation.
        spine._events[0]["timestamp"] = 999.0
        self.assertTrue(spine.verify()["valid"])

    def test_legacy_v1_content_mutation_is_detected(self):
        spine = EventSpine()
        spine._events = [legacy_v1_event(0, "0" * 64, "legacy", "event", {"x": 1}, 1.0)]
        spine.index = {"legacy": [0]}
        spine._events[0]["data"]["x"] = 2
        self.assertFalse(spine.verify()["valid"])

    def test_snapshots_and_append_return_are_defensive_copies(self):
        spine = EventSpine()
        returned = spine.append("epie", "OBSERVED_FACT", {"nested": {"v": [1]}}, timestamp=10.0)
        returned["data"]["nested"]["v"].append(2)
        snapshot = spine.events
        snapshot[0]["data"]["nested"]["v"].append(3)
        recent = spine.recent()
        recent[0]["data"]["nested"]["v"].append(4)
        projection = spine.project("epie")
        projection[0]["data"]["nested"]["v"].append(5)
        replay = spine.replay("epie")
        replay["events"][0]["data"]["nested"]["v"].append(6)
        self.assertEqual(spine.events[0]["data"]["nested"]["v"], [1])
        self.assertTrue(spine.verify()["valid"])

    def test_previous_hash_and_sequence_are_checked(self):
        spine = EventSpine()
        spine.append("epie", "OBSERVED_FACT", {"n": 0})
        spine.append("epie", "EVIDENCE_COMMIT", {"n": 1})
        self.assertTrue(spine.verify()["valid"])
        spine._events[1]["prev_hash"] = "f" * 64
        self.assertFalse(spine.verify()["valid"])

    def test_nonfinite_timestamp_and_non_json_data_are_rejected_before_append(self):
        spine = EventSpine()
        with self.assertRaisesRegex(ValueError, "finite numeric"):
            spine.append("epie", "OBSERVED_FACT", {}, timestamp=math.nan)
        with self.assertRaises(ValueError):
            spine.append("epie", "OBSERVED_FACT", {"bad": math.inf})
        self.assertEqual(len(spine.events), 0)

    def test_invalid_chain_refuses_additional_append(self):
        spine = EventSpine()
        spine.append("epie", "OBSERVED_FACT", {"x": 1})
        spine._events[0]["data"]["x"] = 2
        with self.assertRaisesRegex(ValueError, "invalid event chain"):
            spine.append("epie", "EVIDENCE_COMMIT", {"x": 3})
        self.assertEqual(len(spine.events), 1)

    def test_idempotent_retry_returns_same_event_without_duplicate(self):
        spine = EventSpine()
        first = spine.append("epie", "OBSERVED_FACT", {"x": 1},
                             timestamp=10.0, idempotency_key="same-event")
        retry = spine.append("epie", "OBSERVED_FACT", {"x": 1},
                             timestamp=99.0, idempotency_key="same-event")
        self.assertEqual(first["seq"], retry["seq"])
        self.assertEqual(first["hash"], retry["hash"])
        self.assertEqual(len(spine.events), 1)
        self.assertTrue(spine.verify()["valid"])

    def test_idempotency_key_cannot_be_reused_for_different_content(self):
        spine = EventSpine()
        spine.append("epie", "OBSERVED_FACT", {"x": 1}, idempotency_key="same-event")
        with self.assertRaisesRegex(ValueError, "different event content"):
            spine.append("epie", "OBSERVED_FACT", {"x": 2}, idempotency_key="same-event")
        self.assertEqual(len(spine.events), 1)

    def test_unsupported_hash_version_fails_closed(self):
        spine = EventSpine()
        spine.append("epie", "OBSERVED_FACT", {})
        spine._events[0]["hash_version"] = 99
        self.assertFalse(spine.verify()["valid"])


if __name__ == "__main__":
    unittest.main()
