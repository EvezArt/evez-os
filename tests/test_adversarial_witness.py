import unittest

from src.recursive.adversarial_claim import (
    AdversarialClaimCompiler,
    AttackResult,
    Claim,
    EpistemicState,
)
from src.recursive.challenger import CallableChallenger
from src.recursive.witness import AdversarialWitness


class AdversarialWitnessTests(unittest.TestCase):
    def setUp(self):
        self.claim = Claim(
            "C1",
            "measurement changes the next state",
            "measurement",
            "changes",
            "next-state",
        )

    def test_witness_requires_every_generated_challenge(self):
        challenger = CallableChallenger(
            lambda claim, context: AdversarialClaimCompiler.propose_counter_hypotheses(
                claim,
                (
                    ("no causal effect", 0.0, "null"),
                    ("random effect", 0.5, "noise"),
                ),
            )
        )
        witness = AdversarialWitness(challenger)
        hypotheses = witness.prepare(self.claim)
        report = witness.assess(
            self.claim,
            hypotheses,
            (AttackResult(hypotheses[0].challenge_id, 0.2, 0.2, False, "exp:1"),),
        )
        self.assertFalse(report.structurally_valid)
        self.assertEqual(report.state, EpistemicState.UNKNOWN)

    def test_surviving_claim_is_machine_verifiable(self):
        challenger = CallableChallenger(
            lambda claim, context: AdversarialClaimCompiler.propose_counter_hypotheses(
                claim, (("no causal effect", 0.0, "null"),)
            )
        )
        witness = AdversarialWitness(challenger)
        hypotheses = witness.prepare(self.claim)
        report = witness.assess(
            self.claim,
            hypotheses,
            (AttackResult(hypotheses[0].challenge_id, 0.2, 0.2, False, "exp:1"),),
        )
        self.assertTrue(report.machine_verifiable)
        self.assertEqual(report.state, EpistemicState.SUPPORTED)
        self.assertEqual(len(report.assessment.evidence_hash), 64)


if __name__ == "__main__":
    unittest.main()
