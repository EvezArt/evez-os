"""Small local CLI for the EPIE reference kernel."""
import argparse, json
from .kernel import EventLedger, bayesian_update, entropy_bits, expected_information_gain, rank_tests
from .research import expected_value_of_sample_information, rank_decision_tests, choose_next_test, aggregate_research_reward

def demo():
    prior = {"coordination": .10, "shared_cause": .65, "error": .25}
    evidence = [{"id": "temporal-overlap", "independence_group": "timeline-source-A", "conditional_independence_asserted": True, "likelihoods": {"coordination": .70, "shared_cause": .40, "error": .50}}]
    posterior = bayesian_update(prior, evidence)
    prior2 = {"H1": .20, "H0": .80}
    a = {"id": "test-A", "permitted": True, "value": 1, "cost": 0, "risk": 0, "outcomes": {"positive": {"H1": .80, "H0": .20}, "negative": {"H1": .20, "H0": .80}}}
    b = {"id": "test-B", "permitted": True, "value": 1, "cost": .10, "risk": .20, "outcomes": {"positive": {"H1": .90, "H0": .05}, "negative": {"H1": .10, "H0": .95}}}
    actions = {"act": {"H1": 10.0, "H0": -20.0}, "defer": {"H1": 0.0, "H0": 0.0}}
    decision_rank = rank_decision_tests(prior2, [a, b], actions)
    next_test = choose_next_test(prior2, [a, b], actions, remaining_budget=1.0, steps_completed=0, max_steps=5)
    # Synthetic, deterministic evaluation cohort: 80% positives, 20% negatives.
    # This demonstrates the aggregate gate; it is not an empirical claim.
    heldout_samples = [
        {
            "id": f"demo-case-{i}",
            "independence_key": f"demo-unit-{i}",
            "baseline_forecast": {"positive": .50, "negative": .50},
            "updated_forecast": {"positive": .80, "negative": .20},
            "observed_outcome": "positive" if i < 800 else "negative",
            "verifier_accepted": True,
            "source_independence_verified": True,
            "source_is_duplicate": False,
            "prediction_frozen_before_outcome": True,
            "outcome_held_out": True,
        }
        for i in range(1000)
    ]
    aggregate_reward_demo = aggregate_research_reward(
        heldout_samples,
        search_cost=.10,
        risk_cost=.10,
        projected_future_cases=200.0,
        min_cases=1000,
        alpha=.05,
    )
    return {
        "warning": "Illustrative likelihoods/utilities only; not a real-world finding.",
        "posterior_after_temporal_overlap": posterior,
        "prior_entropy_bits": entropy_bits(prior2),
        "test_A_information_gain_bits": expected_information_gain(prior2, a),
        "test_B_information_gain_bits": expected_information_gain(prior2, b),
        "information_gain_test_ranking": rank_tests(prior2, [a, b]),
        "test_A_EVSI": expected_value_of_sample_information(prior2, a, actions)["expected_value_of_sample_information"],
        "test_B_EVSI": expected_value_of_sample_information(prior2, b, actions)["expected_value_of_sample_information"],
        "decision_value_test_ranking": decision_rank,
        "next_research_decision": {k: v for k, v in next_test.items() if k != "ranking"},
        "illustrative_aggregate_research_reward": aggregate_reward_demo,
    }

def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m evez_epie")
    parser.add_argument("command", choices=("demo", "verify-ledger"))
    parser.add_argument("--ledger", help="JSON file containing an array of ledger events")
    args = parser.parse_args(argv)
    if args.command == "demo":
        print(json.dumps(demo(), indent=2, sort_keys=True)); return 0
    if not args.ledger: parser.error("verify-ledger requires --ledger PATH")
    with open(args.ledger, encoding="utf-8") as handle: events = json.load(handle)
    ledger = EventLedger(events)
    print(json.dumps({"valid": True, "replay": ledger.replay()}, indent=2, sort_keys=True)); return 0
