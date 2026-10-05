import unittest

from mobile.evez_indivifluence import run
from mobile.evez_yhwh import Verdict, judge_context


class SovereignSwarmTests(unittest.TestCase):
    def test_swarm_preserves_multiple_identities(self):
        context = {"swarm": {"seed": "test"}}
        result = run(context, generations=2, size=6)
        first = result["generations"][0]["agents"]
        second = result["generations"][1]["agents"]
        self.assertGreaterEqual(len(first), 6)
        self.assertGreaterEqual(len({item["identity_sha256"] for item in first}), 6)
        self.assertTrue(second)

    def test_swarm_is_deterministic(self):
        context = {"swarm": {"seed": "deterministic"}}
        a = run(context, generations=2, size=5)
        b = run(context, generations=2, size=5)
        self.assertEqual(a["swarm_architecture_sha256"], b["swarm_architecture_sha256"])

    def test_unknown_claim_is_not_promoted(self):
        context = {
            "claims": [{
                "claim_id": "c1",
                "statement": "This system is autonomous and proven.",
                "evidence_state": "UNKNOWN",
            }]
        }
        result = judge_context(context)
        self.assertEqual(result["judgments"][0]["verdict"], Verdict.UNKNOWN.value)

    def test_authority_claim_blocks_without_authorization(self):
        context = {
            "claims": [{
                "claim_id": "c2",
                "statement": "This action is authorized.",
                "claim_type": "authority",
                "evidence_state": "SUPPORTED",
            }]
        }
        result = judge_context(context)
        self.assertEqual(result["judgments"][0]["verdict"], Verdict.BLOCKED.value)

    def test_judge_cannot_self_authorize(self):
        result = judge_context({})
        self.assertEqual(
            result["self_audit"]["verdict"],
            Verdict.HUMILITY_REQUIRED.value,
        )


if __name__ == "__main__":
    unittest.main()
