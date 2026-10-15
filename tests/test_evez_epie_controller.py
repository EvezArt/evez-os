import tempfile
import unittest
from pathlib import Path

from evez_epie import JsonlLedgerStore, ResearchExperimentController


def records(prefix: str, n: int = 2500):
    """Forecast commitment has no outcomes; they are revealed only at settlement."""
    return [{
        "id": f"{prefix}-case-{i}",
        "independence_key": f"{prefix}-unit-{i}",
        "baseline_forecast": {"yes": 0.5, "no": 0.5},
        "updated_forecast": {"yes": 0.8, "no": 0.2},
    } for i in range(n)]


def outcomes(committed, yes_count=2000):
    rows = []
    for i, row in enumerate(committed):
        sample = dict(row)
        sample["observed_outcome"] = "yes" if i < yes_count else "no"
        sample.update({
            "verifier_accepted": True,
            "source_independence_verified": True,
            "source_is_duplicate": False,
            "prediction_frozen_before_outcome": True,
            "outcome_held_out": True,
        })
        rows.append(sample)
    return rows


class ResearchExperimentControllerTests(unittest.TestCase):
    def make_controller(self, path, **overrides):
        settings = {
            "budget_id": "test-budget",
            "initial_budget": 1.0,
            "max_total_credit": 0.015,
            "max_credit_per_trial": 0.01,
            "family_alpha": 0.05,
            "credit_rate": 1.0,
            "min_cases": 1000,
        }
        settings.update(overrides)
        return ResearchExperimentController(JsonlLedgerStore(path), **settings)

    def test_repeated_forecast_commitment_is_idempotent_and_not_double_charged(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctl = self.make_controller(Path(tmp) / "ledger.jsonl")
            forecast = records("cohort-a", 1000)
            first = ctl.reserve(trial_id="trial-a", forecast_records=forecast, search_cost=.01, risk_cost=.01)
            again = ctl.reserve(trial_id="trial-a", forecast_records=forecast, search_cost=.01, risk_cost=.01)
            self.assertEqual(first["decision"], "RESERVED")
            self.assertEqual(again["decision"], "ALREADY_RESERVED")
            self.assertEqual(ctl.status()["reserved_trials"], 1)
            self.assertAlmostEqual(ctl.status()["total_spent"], .02)

    def test_same_holdout_cannot_be_reused_for_adaptive_trials(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctl = self.make_controller(Path(tmp) / "ledger.jsonl")
            forecast = records("same-cohort", 1000)
            ctl.reserve(trial_id="trial-a", forecast_records=forecast, search_cost=.001, risk_cost=.001)
            with self.assertRaisesRegex(ValueError, "cohort already used"):
                ctl.reserve(trial_id="trial-b", forecast_records=forecast, search_cost=.001, risk_cost=.001)

    def test_reserve_rejects_outcomes_before_prediction_commitment(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctl = self.make_controller(Path(tmp) / "ledger.jsonl")
            forecast = records("cohort-a", 10)
            forecast[0]["observed_outcome"] = "yes"
            with self.assertRaisesRegex(ValueError, "before observed outcomes"):
                ctl.reserve(trial_id="trial-a", forecast_records=forecast, search_cost=.01, risk_cost=0)

    def test_precommitted_forecasts_must_match_on_settlement(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctl = self.make_controller(Path(tmp) / "ledger.jsonl")
            forecast = records("cohort-a", 1000)
            ctl.reserve(trial_id="trial-a", forecast_records=forecast, search_cost=.001, risk_cost=.001)
            changed = outcomes(forecast)
            changed[0]["updated_forecast"] = {"yes": .99, "no": .01}
            with self.assertRaisesRegex(ValueError, "pre-outcome prediction commitment"):
                ctl.settle(trial_id="trial-a", samples=changed)

    def test_settlement_awards_bounded_credit_once_and_spends_alpha(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            ctl = self.make_controller(path)
            f1 = records("cohort-a", 2500)
            reservation1 = ctl.reserve(trial_id="trial-a", forecast_records=f1, search_cost=.001, risk_cost=.001)
            self.assertAlmostEqual(reservation1["reservation"]["alpha_spending"], .025)
            settled1 = ctl.settle(trial_id="trial-a", samples=outcomes(f1, yes_count=2000))
            self.assertEqual(settled1["decision"], "REWARD_SUPPORTED")
            self.assertGreater(settled1["settlement"]["credit_issued"], 0)
            self.assertLessEqual(settled1["settlement"]["credit_issued"], .01)

            # Exact retry returns the same receipt and does not mint additional credit.
            again = ctl.settle(trial_id="trial-a", samples=outcomes(f1, yes_count=2000))
            self.assertEqual(again["decision"], "ALREADY_SETTLED")
            self.assertAlmostEqual(ctl.status()["total_credit_issued"], settled1["settlement"]["credit_issued"])

            f2 = records("cohort-b", 2500)
            reservation2 = ctl.reserve(trial_id="trial-b", forecast_records=f2, search_cost=.001, risk_cost=.001)
            self.assertAlmostEqual(reservation2["reservation"]["alpha_spending"], .05 / 6)
            settled2 = ctl.settle(trial_id="trial-b", samples=outcomes(f2, yes_count=2000))
            self.assertEqual(settled2["decision"], "REWARD_SUPPORTED")
            status = ctl.status()
            self.assertAlmostEqual(status["total_credit_issued"], .015)
            self.assertAlmostEqual(status["credit_pool_remaining"], 0.0)
            self.assertLessEqual(status["alpha_spent"], .05)
            self.assertGreater(status["remaining_budget"], 0)

            # Even a third statistically improved trial cannot exceed the lifetime credit pool.
            f3 = records("cohort-c", 2500)
            ctl.reserve(trial_id="trial-c", forecast_records=f3, search_cost=.001, risk_cost=.001)
            settled3 = ctl.settle(trial_id="trial-c", samples=outcomes(f3, yes_count=2000))
            self.assertEqual(settled3["settlement"]["credit_issued"], 0.0)
            self.assertEqual(settled3["decision"], "NO_REWARD_CREDIT_POOL_EXHAUSTED")
            self.assertAlmostEqual(ctl.status()["total_credit_issued"], .015)

    def test_failed_verification_gate_pays_cost_but_no_credit(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctl = self.make_controller(Path(tmp) / "ledger.jsonl", min_cases=30)
            forecast = records("cohort-a", 100)
            ctl.reserve(trial_id="trial-a", forecast_records=forecast, search_cost=.01, risk_cost=.02)
            sample_rows = outcomes(forecast, yes_count=80)
            sample_rows[0]["verifier_accepted"] = False
            result = ctl.settle(trial_id="trial-a", samples=sample_rows)
            self.assertEqual(result["settlement"]["credit_issued"], 0.0)
            self.assertEqual(result["decision"], "NO_REWARD_FAILED_EVIDENCE_GATES")
            self.assertAlmostEqual(ctl.status()["total_spent"], .03)
            self.assertAlmostEqual(ctl.status()["total_credit_issued"], 0.0)

    def test_unaffordable_search_stops_without_reserving_trial(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctl = self.make_controller(Path(tmp) / "ledger.jsonl", initial_budget=.001)
            result = ctl.reserve(trial_id="trial-a", forecast_records=records("cohort-a", 10), search_cost=.001, risk_cost=.001)
            self.assertEqual(result["decision"], "STOP")
            self.assertEqual(result["reason"], "BUDGET_EXHAUSTED")
            self.assertEqual(ctl.status()["reserved_trials"], 0)

    def test_budget_policy_cannot_be_reset_on_reopen(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            ctl = self.make_controller(path)
            ctl.status()
            reopened = self.make_controller(path)
            self.assertEqual(reopened.status()["initial_budget"], 1.0)
            changed = self.make_controller(path, initial_budget=1000)
            with self.assertRaisesRegex(ValueError, "policy mismatch"):
                changed.status()

    def test_family_alpha_spending_is_summable(self):
        total = sum(.05 / (i * (i + 1)) for i in range(1, 100000))
        self.assertLessEqual(total, .05)
        self.assertAlmostEqual(.05 / (1 * 2), .025)
        self.assertAlmostEqual(.05 / (2 * 3), .05 / 6)


if __name__ == "__main__":
    unittest.main()
