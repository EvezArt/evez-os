import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reward_loop import EvezBrainRewardLoop


class RewardLoopTests(unittest.TestCase):
    def test_records_event_and_returns_reward(self):
        with tempfile.TemporaryDirectory() as td:
            db = f"{td}/reward.sqlite3"
            loop = EvezBrainRewardLoop(db)
            event = loop.record_action(
                action_type="test_result",
                success=True,
                metadata={"passed": True, "num_tests": 42},
            )
            self.assertEqual(event["action_type"], "test_result")
            self.assertGreater(event["reward"]["total"], 0)

    def test_decision_profile_prefers_higher_reward_actions(self):
        with tempfile.TemporaryDirectory() as td:
            db = f"{td}/reward.sqlite3"
            loop = EvezBrainRewardLoop(db)
            for _ in range(6):
                loop.record_action("pr_merge", True, {"review_score": 0.5, "tests_green": True})
            for _ in range(6):
                loop.record_action("api_call", False, {"status_code": 500, "latency_ms": 1000})

            profile = loop.decision_profile(candidates=["pr_merge", "api_call"], lookback=100)
            self.assertEqual(profile["recommended_action"], "pr_merge")
            self.assertGreater(profile["objective_means"]["code_quality"], 0)


if __name__ == "__main__":
    unittest.main()
