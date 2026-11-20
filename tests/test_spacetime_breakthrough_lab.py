import json
import tempfile
import unittest
from pathlib import Path

from research.spacetime_breakthrough_lab import (
    LabError, append_event, experiment_summary, new_experiment,
    validate_observation, validate_experiment, verify_ledger,
)


class SpacetimeBreakthroughLabTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ledger = Path(self.temp.name) / "spacetime.jsonl"
        self.experiment = new_experiment(
            title="Metric candidate audit",
            hypothesis="A specified metric ansatz satisfies listed symbolic constraints under explicit assumptions.",
            model_name="symbolic-metric-screen-v1",
            assumptions=["Coordinates and metric signature are stated."],
            predictions=["Independent implementation reproduces tensor components."],
            controls=["Compare the zero-parameter limit against flat spacetime."],
        )

    def register(self):
        append_event(self.ledger, {"event_type": "SPACETIME_LAB.EXPERIMENT_REGISTERED", "experiment": self.experiment})

    def test_register_then_verify_empty_observation_set(self):
        self.register()
        result = verify_ledger(self.ledger)
        self.assertTrue(result["ok"])
        self.assertEqual(result["events"], 1)
        summary = experiment_summary(self.ledger)
        self.assertEqual(summary["experiment"]["epistemic_status"], "PROPOSED")
        self.assertEqual(summary["observations"], [])

    def test_observation_appends_to_hash_chain(self):
        self.register()
        obs = {
            "source": "local-simulator", "modality": "simulation", "quantity": "constraint_residual",
            "value": 1.25e-9, "unit": "dimensionless", "uncertainty": 0.0,
            "calibration_id": "sim-build-abc123", "evidence_uri": None, "evidence_sha256": None,
            "notes": "Synthetic example; not a physical measurement.", "observed_at": "2026-10-11T00:00:00Z"
        }
        validate_observation(obs)
        append_event(self.ledger, {"event_type": "SPACETIME_LAB.OBSERVATION_RECORDED", "observation": obs})
        summary = experiment_summary(self.ledger)
        self.assertTrue(summary["verification"]["ok"])
        self.assertEqual(len(summary["observations"]), 1)
        self.assertEqual(summary["observations"][0]["value"], 1.25e-9)

    def test_refuses_observation_without_registered_experiment(self):
        obs = {"source":"s","modality":"simulation","quantity":"q","value":1,"unit":"u","calibration_id":"c","observed_at":"now"}
        with self.assertRaises(LabError):
            append_event(self.ledger, {"event_type":"SPACETIME_LAB.OBSERVATION_RECORDED","observation":obs})

    def test_refuses_second_experiment_in_same_ledger(self):
        self.register()
        with self.assertRaises(LabError):
            append_event(self.ledger, {"event_type":"SPACETIME_LAB.EXPERIMENT_REGISTERED","experiment":self.experiment})

    def test_refuses_unknown_modality(self):
        with self.assertRaises(LabError):
            validate_observation({"source":"s","modality":"mind-reading","quantity":"q","value":1,"unit":"u","calibration_id":"none","observed_at":"now"})

    def test_speculative_claim_requires_interpretation_limits(self):
        experiment = dict(self.experiment)
        experiment["safety_limits"] = []
        with self.assertRaises(LabError):
            validate_experiment(experiment)

    def test_tampering_is_detected(self):
        self.register()
        lines = self.ledger.read_text(encoding="utf-8").splitlines()
        record = json.loads(lines[0])
        record["event"]["experiment"]["hypothesis"] = "changed after the fact"
        lines[0] = json.dumps(record)
        self.ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = verify_ledger(self.ledger)
        self.assertFalse(result["ok"])
        self.assertIn("hash mismatch", result["error"])

    def test_refuses_to_extend_corrupted_chain(self):
        self.register()
        self.ledger.write_text(self.ledger.read_text(encoding="utf-8") + "{}\n", encoding="utf-8")
        with self.assertRaises(LabError):
            append_event(self.ledger, {"event_type":"SPACETIME_LAB.ANALYSIS_NOTE","note":"do not append"})

    def test_review_does_not_promote_scientific_status(self):
        self.register()
        append_event(self.ledger, {"event_type":"SPACETIME_LAB.REVIEW_RECORDED","reviewer":"reviewer-1","decision":"accept-method","notes":"Method only"})
        self.assertEqual(experiment_summary(self.ledger)["experiment"]["epistemic_status"], "PROPOSED")


if __name__ == "__main__":
    unittest.main()
