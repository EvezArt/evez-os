import unittest

from src.recursive.adversarial_claim import (
    AdversarialClaimCompiler,
    AttackResult,
    Claim,
    EpistemicState,
    finalize_assessment,
)
from src.recursive.challenger import build_challenge_plan, validate_attack_set


class AdversarialClaimTests(unittest.TestCase):
    def setUp(self):
        self.claim = Claim(
            "C1",
            "measurement back-action changes the next state",
            "measurement",
            "changes",
            "next-state",
        )

    def test_no_attack_means_unknown(self):
        result = AdversarialClaimCompiler().assess(self.claim, (), ())
        self.assertEqual(result.state, EpistemicState.UNKNOWN)

    def test_clean_attack_yields_supported(self):
        hypotheses = AdversarialClaimCompiler.propose_counter_hypotheses(
            self.claim, (("measurement has no causal effect", 0.0, "null model"),)
        )
        attacks = (
            AttackResult(
                hypotheses[0].challenge_id, 0.2, 0.2, False, "experiment:1"
            ),
        )
        result = AdversarialClaimCompiler().assess(
            self.claim, hypotheses, attacks
        )
        self.assertEqual(result.state, EpistemicState.SUPPORTED)

    def test_contradiction_wins(self):
        hypotheses = AdversarialClaimCompiler.propose_counter_hypotheses(
            self.claim, (("null model", 0.0, "challenge"),)
        )
        attacks = (
            AttackResult(
                hypotheses[0].challenge_id, 0.0, 0.0, True, "experiment:2"
            ),
        )
        result = AdversarialClaimCompiler().assess(
            self.claim, hypotheses, attacks
        )
        self.assertEqual(result.state, EpistemicState.CONTRADICTED)

    def test_finalization_hashes_assessment(self):
        result = AdversarialClaimCompiler().assess(self.claim, (), ())
        finalized = finalize_assessment(result)
        self.assertEqual(len(finalized.evidence_hash), 64)

    def test_attack_validator_is_fail_closed(self):
        hypotheses = AdversarialClaimCompiler.propose_counter_hypotheses(
            self.claim, (("null model", 0.0, "challenge"),)
        )
        plan = build_challenge_plan(self.claim, hypotheses)
        ok, _ = validate_attack_set(
            plan, (AttackResult("bogus", 0.0, 0.0, False, "x"),)
        )
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
