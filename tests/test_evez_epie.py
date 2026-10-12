import math, struct, unittest
from evez_epie.kernel import EventLedger, bayesian_update, entropy_bits, expected_information_gain, rank_retention, retention_score, canonical_json, canonical_hash
from evez_epie.retention import select_hot_index
from evez_epie.research import expected_value_of_sample_information, rank_decision_tests, choose_next_test, prequential_log_score, realized_research_reward, aggregate_research_reward

class CanonicalizationTests(unittest.TestCase):
    def test_jcs_number_and_utf16_key_canonicalization(self):
        self.assertEqual(canonical_json({"z": 1.0, "a": -0.0}), '{"a":0,"z":1}')
        keys = {chr(0xE000): 1, chr(0x10000): 2}
        expected = '{"' + chr(0x10000) + '":2,"' + chr(0xE000) + '":1}'
        self.assertEqual(canonical_json(keys), expected)
        self.assertEqual(len(canonical_hash({"stable": [1, True, None]})), 64)

    def test_rfc8785_number_serialization_vectors(self):
        # Selected IEEE-754 vectors from RFC 8785 Appendix B.
        vectors = {
            "0000000000000000": "0",
            "8000000000000000": "0",
            "0000000000000001": "5e-324",
            "8000000000000001": "-5e-324",
            "7fefffffffffffff": "1.7976931348623157e+308",
            "ffefffffffffffff": "-1.7976931348623157e+308",
            "4430000000000000": "295147905179352830000",
            "44b52d02c7e14af5": "9.999999999999997e+22",
            "44b52d02c7e14af6": "1e+23",
            "44b52d02c7e14af7": "1.0000000000000001e+23",
            "444b1ae4d6e2ef4e": "999999999999999700000",
            "444b1ae4d6e2ef4f": "999999999999999900000",
            "444b1ae4d6e2ef50": "1e+21",
            "3eb0c6f7a0b5ed8c": "9.999999999999997e-7",
            "3eb0c6f7a0b5ed8d": "0.000001",
            "43143ff3c1cb0959": "1424953923781206.2",
        }
        for bits, expected in vectors.items():
            value = struct.unpack(">d", bytes.fromhex(bits))[0]
            with self.subTest(bits=bits):
                self.assertEqual(canonical_json(value), expected)

    def test_rfc8785_composite_example(self):
        value = "€$" + chr(0x0F) + "\nA'B" + '"' + "\\" + "\\" + '"' + "/"
        expected_string = '"' + "€$" + r'\u000f' + r'\n' + "A'B" + r'\"' + r'\\\\' + r'\"' + "/" + '"'
        obj = {"numbers": [333333333.33333329, 1e30, 4.50, 2e-3, 1e-27], "string": value, "literals": [None, True, False]}
        expected = '{"literals":[null,true,false],"numbers":[333333333.3333333,1e+30,4.5,0.002,1e-27],"string":' + expected_string + '}'
        self.assertEqual(canonical_json(obj), expected)


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
    def test_zero_likelihood_can_falsify_one_hypothesis(self):
        prior = {"H1": .2, "H0": .8}
        evidence = [{
            "id": "decisive-evidence",
            "independence_group": "source-x",
            "conditional_independence_asserted": True,
            "likelihoods": {"H1": 0.0, "H0": .5},
        }]
        got = bayesian_update(prior, evidence)
        self.assertEqual(got, {"H0": 1.0, "H1": 0.0})

    def test_zero_likelihood_for_every_hypothesis_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "zero posterior support"):
            bayesian_update({"H1": .2, "H0": .8}, [{
                "id": "impossible-evidence",
                "independence_group": "source-x",
                "conditional_independence_asserted": True,
                "likelihoods": {"H1": 0.0, "H0": 0.0},
            }])

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

class DecisionValueResearchTests(unittest.TestCase):
    def setUp(self):
        self.prior = {"H1": .20, "H0": .80}
        self.actions = {
            "act": {"H1": 10.0, "H0": -20.0},
            "defer": {"H1": 0.0, "H0": 0.0},
        }
        self.test_a = {
            "id": "A", "permitted": True, "cost": 0.0, "risk": 0.0,
            "outcomes": {
                "positive": {"H1": .80, "H0": .20},
                "negative": {"H1": .20, "H0": .80},
            },
        }
        self.test_b = {
            "id": "B", "permitted": True, "cost": .10, "risk": .20,
            "outcomes": {
                "positive": {"H1": .90, "H0": .05},
                "negative": {"H1": .10, "H0": .95},
            },
        }

    def test_evsi_rewards_decision_improvement_not_entropy_alone(self):
        result_a = expected_value_of_sample_information(self.prior, self.test_a, self.actions)
        result_b = expected_value_of_sample_information(self.prior, self.test_b, self.actions)
        self.assertAlmostEqual(result_a["expected_value_of_sample_information"], 0.0, places=12)
        self.assertAlmostEqual(result_b["expected_value_of_sample_information"], 1.0, places=12)
        self.assertEqual(result_a["best_action_before_test"], "defer")
        self.assertEqual(result_b["best_action_before_test"], "defer")

    def test_net_value_ranks_test_b_first(self):
        rows = rank_decision_tests(self.prior, [self.test_a, self.test_b], self.actions)
        self.assertEqual(rows[0]["id"], "B")
        self.assertAlmostEqual(rows[0]["net_value"], .70, places=12)

    def test_stop_gate_enforces_budget_and_finite_steps(self):
        stopped = choose_next_test(self.prior, [self.test_b], self.actions,
                                   remaining_budget=1.0, steps_completed=3, max_steps=3)
        self.assertEqual(stopped["decision"], "STOP")
        self.assertEqual(stopped["reason"], "MAX_STEPS_REACHED")
        unaffordable = choose_next_test(self.prior, [self.test_b], self.actions,
                                        remaining_budget=.05, steps_completed=0, max_steps=5)
        self.assertEqual(unaffordable["decision"], "STOP")
        self.assertEqual(unaffordable["reason"], "NO_PERMITTED_AFFORDABLE_TEST")

    def test_unpermitted_test_is_never_ranked(self):
        forbidden = dict(self.test_b, permitted=False)
        rows = rank_decision_tests(self.prior, [forbidden], self.actions)
        self.assertEqual(rows, [])

class ResearchRewardTests(unittest.TestCase):
    def test_reward_requires_verified_independent_holdout_improvement(self):
        result = realized_research_reward(
            {"yes": .5, "no": .5},
            {"yes": .8, "no": .2},
            "yes",
            search_cost=.1,
            risk_cost=.1,
            verifier_accepted=True,
            source_independence_verified=True,
            source_is_duplicate=False,
            prediction_frozen_before_outcome=True,
            outcome_held_out=True,
        )
        self.assertTrue(result["eligible"])
        self.assertAlmostEqual(result["score_delta"], math.log(1.6), places=12)
        self.assertAlmostEqual(result["net_reward"], math.log(1.6) - .2, places=12)

    def test_unverified_or_duplicate_search_cannot_earn_positive_reward(self):
        result = realized_research_reward(
            {"yes": .5, "no": .5},
            {"yes": .99, "no": .01},
            "yes",
            search_cost=.1,
            risk_cost=.2,
            verifier_accepted=False,
            source_independence_verified=False,
            source_is_duplicate=True,
            prediction_frozen_before_outcome=False,
            outcome_held_out=False,
        )
        self.assertFalse(result["eligible"])
        self.assertIsNone(result["score_delta"])
        self.assertEqual(result["net_reward"], -.3)
        self.assertIn("verifier_accepted", result["failed_gates"])
        self.assertIn("source_is_not_duplicate", result["failed_gates"])

    def test_log_score_uses_fixed_floor_for_zero_probability(self):
        self.assertAlmostEqual(prequential_log_score({"yes": 0.0, "no": 1.0}, "yes"), math.log(1e-12), places=12)

    def test_log_score_rejects_unnormalized_forecast(self):
        with self.assertRaisesRegex(ValueError, "sum to"):
            prequential_log_score({"yes": 2.0, "no": 2.0}, "yes")

    def test_log_score_rejects_boolean_probability(self):
        with self.assertRaisesRegex(ValueError, "numeric, not booleans"):
            prequential_log_score({"yes": True, "no": 0.0}, "yes")

class AggregateResearchRewardTests(unittest.TestCase):
    @staticmethod
    def cases(outcomes, *, forecast_after=None, gate_override=None):
        rows = []
        for i, outcome in enumerate(outcomes):
            row = {
                "id": f"case-{i}",
                "independence_key": f"unit-{i}",
                "baseline_forecast": {"yes": .5, "no": .5},
                "updated_forecast": forecast_after or {"yes": .8, "no": .2},
                "observed_outcome": outcome,
                "verifier_accepted": True,
                "source_independence_verified": True,
                "source_is_duplicate": False,
                "prediction_frozen_before_outcome": True,
                "outcome_held_out": True,
            }
            if gate_override and i == gate_override[0]:
                row[gate_override[1]] = gate_override[2]
            rows.append(row)
        return rows

    def test_reward_requires_positive_heldout_lower_bound_after_cost(self):
        outcomes = ["yes"] * 800 + ["no"] * 200
        result = aggregate_research_reward(
            self.cases(outcomes),
            search_cost=2.0,
            risk_cost=1.0,
            projected_future_cases=200.0,
            min_cases=1000,
            alpha=.05,
        )
        self.assertEqual(result["status"], "REWARD_SUPPORTED")
        self.assertAlmostEqual(result["mean_score_delta"], .18, places=12)
        self.assertGreater(result["lower_confidence_bound"], 0)
        self.assertGreater(result["net_reward"], 0)

    def test_no_holdout_improvement_receives_no_gross_reward(self):
        outcomes = ["yes"] * 400 + ["no"] * 100
        result = aggregate_research_reward(
            self.cases(outcomes, forecast_after={"yes": .5, "no": .5}),
            search_cost=2.0, risk_cost=1.0,
            projected_future_cases=200.0, min_cases=500,
        )
        self.assertEqual(result["status"], "NO_REWARD_GAIN_NOT_PROVEN")
        self.assertEqual(result["gross_reward"], 0.0)
        self.assertEqual(result["net_reward"], -3.0)

    def test_one_failed_evidence_gate_blocks_reward(self):
        outcomes = ["yes"] * 800 + ["no"] * 200
        result = aggregate_research_reward(
            self.cases(outcomes, gate_override=(19, "source_is_duplicate", True)),
            search_cost=1.0, risk_cost=2.0,
            projected_future_cases=100.0, min_cases=1000,
        )
        self.assertEqual(result["status"], "NO_REWARD_FAILED_EVIDENCE_GATES")
        self.assertEqual(result["gross_reward"], 0.0)
        self.assertEqual(result["net_reward"], -3.0)
        self.assertIn("case-19:source_is_not_duplicate", result["failed_gates"])

    def test_repeated_independence_unit_is_rejected(self):
        rows = self.cases(["yes"] * 30)
        rows[1]["independence_key"] = rows[0]["independence_key"]
        with self.assertRaisesRegex(ValueError, "Repeated independence_key"):
            aggregate_research_reward(rows, search_cost=1.0, risk_cost=0.0, min_cases=30)

    def test_too_few_cases_does_not_earn_reward(self):
        result = aggregate_research_reward(
            self.cases(["yes"] * 10),
            search_cost=1.0, risk_cost=.5, min_cases=30,
        )
        self.assertEqual(result["status"], "NO_REWARD_INSUFFICIENT_HOLDOUT")
        self.assertEqual(result["net_reward"], -1.5)

class LedgerTests(unittest.TestCase):
    def test_chain_and_replay(self):
        ledger=EventLedger(); ledger.append("OBSERVED_FACT",{"claim_status":"REPORTED"}); ledger.append("EVIDENCE_COMMIT",{"source_hash":"abc"})
        self.assertEqual(ledger.verify(),(True,"ok")); self.assertEqual(ledger.replay()["event_count"],2)
    def test_returned_objects_cannot_mutate_internal_ledger(self):
        ledger = EventLedger()
        returned = ledger.append("OBSERVED_FACT", {"nested": {"values": [1]}})
        returned["payload"]["nested"]["values"].append(2)
        snapshot = ledger.events
        snapshot[0]["payload"]["nested"]["values"].append(3)
        replay = ledger.replay()
        replay["committed_payloads"][0]["payload"]["nested"]["values"].append(4)
        self.assertEqual(ledger.verify(), (True, "ok"))
        self.assertEqual(ledger.events[0]["payload"]["nested"]["values"], [1])

    def test_mutation_detected(self):
        ledger=EventLedger(); ledger.append("OBSERVED_FACT",{"x":1}); events=[dict(e) for e in ledger.events]; events[0]["payload"]["x"]=2
        with self.assertRaisesRegex(ValueError,"Invalid initial ledger"): EventLedger(events)
    def test_unknown_event_type_rejected(self):
        with self.assertRaisesRegex(ValueError,"Unsupported event type"): EventLedger().append("HYPOTHESIS_GENERATED",{})

if __name__ == "__main__": unittest.main()
