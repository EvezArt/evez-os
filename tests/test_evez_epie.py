import math, unittest
from evez_epie.kernel import EventLedger, bayesian_update, entropy_bits, expected_information_gain, rank_retention, retention_score
from evez_epie.retention import select_hot_index
from evez_epie.retention import select_hot_index

class BayesianTests(unittest.TestCase):
    def test_temporal_overlap_example(self):
        prior = {"coordination": .10, "shared": .65, "error": .25}
        ev = [{"id":"e1", "independence_group":"source-1", "conditional_independence_asserted":True, "likelihoods":{"coordination":.70,"shared":.40,"error":.50}}]
        got = bayesian_update(prior, ev)
        self.assertAlmostEqual(got["coordination"], .070/.455, places=12)
        self.assertAlmostEqual(math.fsum(got.values()), 1.0, places=12)
    def test_duplicate_dependence_group_rejected(self):
        prior = {"H1": .2, "H0": .8}; base = {"independence_group":"same", "conditional_independence_asserted":True, "likelihoods":{"H1":.8,"H0":.2}}
        with self.assertRaisesRegex(ValueError, "Repeated dependence group"): bayesian_update(prior, [dict(base,id="a"),dict(base,id="b")])
    def test_independence_must_be_explicit(self):
        with self.assertRaisesRegex(ValueError, "not declared"): bayesian_update({"H":1.0}, [{"id":"e","independence_group":"g","conditional_independence_asserted":False,"likelihoods":{"H":.5}}])
    def test_entropy(self): self.assertAlmostEqual(entropy_bits({"H1":.2,"H0":.8}), .7219280948873623)
    def test_information_gain(self):
        p={"H1":.2,"H0":.8}
        a={"outcomes":{"positive":{"H1":.8,"H0":.2},"negative":{"H1":.2,"H0":.8}}}
        b={"outcomes":{"positive":{"H1":.9,"H0":.05},"negative":{"H1":.1,"H0":.95}}}
        iga,igb=expected_information_gain(p,a),expected_information_gain(p,b)
        self.assertAlmostEqual(iga,.18245,places=4); self.assertAlmostEqual(igb,.43725,places=4); self.assertGreater(igb,iga)

class RetentionTests(unittest.TestCase):
    def test_decay_is_priority_not_truth(self):
        recent=retention_score(decision_value=1,reliability=.9,novelty=1,age_seconds=0,half_life_seconds=100)
        old=retention_score(decision_value=1,reliability=.9,novelty=1,age_seconds=100,half_life_seconds=100)
        self.assertAlmostEqual(old,recent/2)
        durable=retention_score(decision_value=1,reliability=.9,novelty=1,age_seconds=100000,half_life_seconds=None)
        self.assertAlmostEqual(durable,.9)
    def test_duplicate_hash_dedupes_index_only(self):
        base={"created_at_seconds":90,"content_hash":"same","decision_value":1,"reliability":1,"novelty":1,"half_life_seconds":None,"storage_bytes":100}
        rows=rank_retention([dict(base,id="a"),dict(base,id="b")],now_seconds=100)
        self.assertEqual(len(rows),2); self.assertTrue(all("KEEP_SOURCE_REFERENCE" in r["action"] for r in rows))

class BudgetedRetentionTests(unittest.TestCase):
    def test_knapsack_selects_max_utility_within_budget_and_dedupes_bytes(self):
        items = [
            {"id":"a", "content_hash":"ha", "created_at_seconds":100, "storage_bytes":6, "decision_value":8, "reliability":1, "novelty":1, "half_life_seconds":None},
            {"id":"b", "content_hash":"hb", "created_at_seconds":100, "storage_bytes":5, "decision_value":6, "reliability":1, "novelty":1, "half_life_seconds":None},
            {"id":"a-copy", "content_hash":"ha", "created_at_seconds":100, "storage_bytes":6, "decision_value":2, "reliability":1, "novelty":1, "half_life_seconds":None},
        ]
        result = select_hot_index(items, budget_bytes=11, now_seconds=100)
        self.assertEqual(result["used_bytes"], 11)
        self.assertEqual(result["retained_utility"], 14)
        self.assertEqual(result["selected_source_ids"], ["a", "a-copy", "b"])
        self.assertEqual(result["archival_only_source_ids"], [])

    def test_unselected_artifact_is_archival_not_deleted(self):
        items = [
            {"id":"large", "created_at_seconds":0, "storage_bytes":10, "decision_value":1, "reliability":1, "novelty":1, "half_life_seconds":None},
            {"id":"small", "created_at_seconds":0, "storage_bytes":2, "decision_value":2, "reliability":1, "novelty":1, "half_life_seconds":None},
        ]
        result = select_hot_index(items, budget_bytes=2, now_seconds=0)
        self.assertEqual(result["selected_source_ids"], ["small"])
        self.assertEqual(result["archival_only_source_ids"], ["large"])

class LedgerTests(unittest.TestCase):
    def test_chain_and_replay(self):
        ledger=EventLedger(); ledger.append("OBSERVED_FACT",{"claim_status":"REPORTED"}); ledger.append("EVIDENCE_COMMIT",{"source_hash":"abc"})
        self.assertEqual(ledger.verify(),(True,"ok")); self.assertEqual(ledger.replay()["event_count"],2)
    def test_mutation_detected(self):
        ledger=EventLedger(); ledger.append("OBSERVED_FACT",{"x":1}); events=[dict(e) for e in ledger.events]; events[0]["payload"]["x"]=2
        with self.assertRaisesRegex(ValueError,"Invalid initial ledger"): EventLedger(events)
    def test_unknown_event_type_rejected(self):
        with self.assertRaisesRegex(ValueError,"Unsupported event type"): EventLedger().append("HYPOTHESIS_GENERATED",{})

if __name__ == "__main__": unittest.main()
