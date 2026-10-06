import unittest

from src.recursive.active_lab import ActiveMeasurementLab
from src.recursive.experiment_protocol import chain
from src.recursive.phenomenon_engine import PhenomenonEngine, PhenomenonState
from src.recursive.witness import verify_chain, verify_record


class WitnessTests(unittest.TestCase):
    def test_independent_witness_accepts_valid_record(self):
        lab = ActiveMeasurementLab(
            PhenomenonEngine(PhenomenonState((0.1, 0.2)))
        )
        lab.step()
        findings = verify_record(lab.records[0])
        self.assertTrue(all(item.ok for item in findings))

    def test_independent_witness_recomputes_influence(self):
        lab = ActiveMeasurementLab(
            PhenomenonEngine(PhenomenonState((0.1, 0.2)))
        )
        lab.step()
        original = lab.records[0]
        corrupted = type(original)(
            **{
                **original.__dict__,
                "measurement_influence": original.measurement_influence + 1.0,
            }
        )
        findings = verify_record(corrupted)
        self.assertTrue(any(item.code == "INFLUENCE_MISMATCH" for item in findings))

    def test_chain_witness_detects_broken_parent(self):
        lab = ActiveMeasurementLab(
            PhenomenonEngine(PhenomenonState((0.1, 0.2)))
        )
        lab.run(2)
        records = list(lab.records)
        records[1] = type(records[1])(
            **{**records[1].__dict__, "parent_hash": "tampered"}
        )
        findings = verify_chain(records)
        self.assertTrue(any(item.code == "BROKEN_PARENT_CHAIN" for item in findings))

    def test_chain_witness_accepts_chained_records(self):
        lab = ActiveMeasurementLab(
            PhenomenonEngine(PhenomenonState((0.1, 0.2)))
        )
        lab.run(3)
        findings = verify_chain(lab.records)
        self.assertTrue(any(item.code == "CHAIN_VALID" for item in findings))


if __name__ == "__main__":
    unittest.main()
