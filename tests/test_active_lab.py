import unittest

from src.recursive.active_lab import ActiveMeasurementLab
from src.recursive.armor_charmer import ArmorCharmer, ProposedAction, RiskClass
from src.recursive.phenomenon_engine import EngineConfig, PhenomenonEngine, PhenomenonState


class ActiveMeasurementLabTests(unittest.TestCase):
    def test_records_form_a_hash_chain(self):
        engine = PhenomenonEngine(
            PhenomenonState((0.2, 0.4)),
            EngineConfig(max_steps=3),
        )
        lab = ActiveMeasurementLab(engine, run_id="chain-test")
        lab.run(3)
        records = lab.records

        self.assertEqual(records[0].parent_hash, "genesis")
        self.assertEqual(records[1].parent_hash, records[0].content_hash())
        self.assertEqual(records[2].parent_hash, records[1].content_hash())

    def test_external_authorization_is_separate_from_execution(self):
        lab = ActiveMeasurementLab(
            PhenomenonEngine(PhenomenonState((0.1, 0.2)))
        )
        proposal = ProposedAction(
            "open-browser",
            RiskClass.EXTERNAL,
            reversible=True,
            side_effect=True,
            scope="browser",
        )
        decision = lab.authorize_external(proposal)
        self.assertFalse(decision.allowed)

    def test_event_projection_preserves_hash(self):
        lab = ActiveMeasurementLab(
            PhenomenonEngine(PhenomenonState((0.1, 0.2)))
        )
        lab.step()
        event = lab.event_stream()[0]
        self.assertEqual(event["content_hash"], lab.records[0].content_hash())


if __name__ == "__main__":
    unittest.main()
