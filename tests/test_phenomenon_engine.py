import unittest

from src.recursive.phenomenon_engine import (
    EngineConfig,
    PhenomenonEngine,
    PhenomenonState,
)


class PhenomenonEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = PhenomenonEngine(
            PhenomenonState((0.2, 0.4, 0.6, 0.8)),
            EngineConfig(max_steps=8),
        )

    def test_measurement_has_causal_influence(self):
        transition = self.engine.step()
        self.assertGreater(transition.influence, 0.0)
        self.assertNotEqual(
            transition.observed_state.values,
            transition.counterfactual_state.values,
        )

    def test_observable_enters_next_state(self):
        transition = self.engine.step()
        self.assertEqual(transition.observation.channel, "mean-state")
        self.assertGreater(transition.observation.value, 0.0)
        self.assertEqual(transition.observed_state.tick, 1)

    def test_models_update(self):
        before = [(m.slope, m.intercept) for m in self.engine.hypotheses]
        self.engine.step()
        after = [(m.slope, m.intercept) for m in self.engine.hypotheses]
        self.assertNotEqual(before, after)

    def test_recursive_run_records_every_transition(self):
        transitions = self.engine.run(5)
        self.assertEqual(len(transitions), 5)
        self.assertEqual(len(self.engine.history), 5)
        self.assertEqual(self.engine.state.tick, 5)

    def test_snapshot_hash_is_stable_for_unchanged_state(self):
        first = self.engine.hash_snapshot()
        second = self.engine.hash_snapshot()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
