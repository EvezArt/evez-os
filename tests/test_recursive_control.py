import unittest

from src.recursive.armor_charmer import (
    ArmorCharmer,
    ProposedAction,
    RiskClass,
)
from src.recursive.falsification import (
    FalsificationRule,
    HypothesisView,
    rank_candidates,
    should_falsify,
)


class RecursiveControlTests(unittest.TestCase):
    def test_simulation_is_allowed_without_capability(self):
        decision = ArmorCharmer().authorize(
            ProposedAction("dry-run", RiskClass.SIMULATE)
        )
        self.assertTrue(decision.allowed)
        self.assertFalse(decision.requires_human)

    def test_external_action_fails_closed(self):
        decision = ArmorCharmer().authorize(
            ProposedAction(
                "browser-click",
                RiskClass.EXTERNAL,
                reversible=True,
                side_effect=True,
                scope="browser",
            )
        )
        self.assertFalse(decision.allowed)
        self.assertIn("missing explicit capability", decision.reason)

    def test_irreversible_action_requires_capability_and_human(self):
        gate = ArmorCharmer(frozenset({"irreversible:deploy"}))
        denied = gate.authorize(
            ProposedAction(
                "deploy",
                RiskClass.IRREVERSIBLE,
                reversible=False,
                side_effect=True,
                scope="deploy",
            )
        )
        self.assertFalse(denied.allowed)
        self.assertTrue(denied.requires_human)

        approved = gate.authorize(
            ProposedAction(
                "deploy",
                RiskClass.IRREVERSIBLE,
                reversible=False,
                side_effect=True,
                scope="deploy",
            ),
            {"human_authorized": True},
        )
        self.assertTrue(approved.allowed)

    def test_discriminator_prefers_model_separation(self):
        models = (
            HypothesisView("slow", lambda state, action: action * 0.5),
            HypothesisView("fast", lambda state, action: action * 1.5),
        )
        ranked = rank_candidates((1.0,), models, (-0.1, 0.2, 1.0))
        self.assertEqual(ranked[0].action_value, 1.0)
        self.assertGreater(ranked[0].disagreement, ranked[-1].disagreement)

    def test_falsification_rule_is_explicit(self):
        rule = FalsificationRule("M1", max_abs_error=0.25)
        self.assertFalse(should_falsify((rule,), "M1", 0.20))
        self.assertTrue(should_falsify((rule,), "M1", 0.30))
        self.assertFalse(should_falsify((rule,), "M2", 99.0))


if __name__ == "__main__":
    unittest.main()
