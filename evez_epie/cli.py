"""Local-first CLI for EPIE inference, durable ledger, and explicit spine sync."""
from __future__ import annotations

import argparse
import json

from .kernel import EVENT_TYPES, entropy_bits, expected_information_gain, rank_tests, bayesian_update
from .research import (
    aggregate_research_reward,
    choose_next_test,
    expected_value_of_sample_information,
    rank_decision_tests,
)
from .spine_adapter import DEFAULT_SPINE_URL, sync_ledger_to_spine, verify_spine
from .store import JsonlLedgerStore
from .experiment_controller import ResearchExperimentController


def demo():
    prior = {"coordination": .10, "shared_cause": .65, "error": .25}
    evidence = [{
        "id": "temporal-overlap",
        "independence_group": "timeline-source-A",
        "conditional_independence_asserted": True,
        "likelihoods": {"coordination": .70, "shared_cause": .40, "error": .50},
    }]
    posterior = bayesian_update(prior, evidence)
    prior2 = {"H1": .20, "H0": .80}
    a = {
        "id": "test-A", "permitted": True, "value": 1, "cost": 0, "risk": 0,
        "outcomes": {"positive": {"H1": .80, "H0": .20},
                     "negative": {"H1": .20, "H0": .80}},
    }
    b = {
        "id": "test-B", "permitted": True, "value": 1, "cost": .10, "risk": .20,
        "outcomes": {"positive": {"H1": .90, "H0": .05},
                     "negative": {"H1": .10, "H0": .95}},
    }
    actions = {"act": {"H1": 10.0, "H0": -20.0},
               "defer": {"H1": 0.0, "H0": 0.0}}
    decision_rank = rank_decision_tests(prior2, [a, b], actions)
    next_test = choose_next_test(
        prior2, [a, b], actions, remaining_budget=1.0,
        steps_completed=0, max_steps=5,
    )

    # Synthetic deterministic evaluation cohort, not empirical evidence.
    heldout_samples = [{
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
    } for i in range(1000)]
    aggregate_reward_demo = aggregate_research_reward(
        heldout_samples, search_cost=.10, risk_cost=.10,
        projected_future_cases=200.0, min_cases=1000, alpha=.05,
    )
    return {
        "warning": "Illustrative priors, likelihoods, utilities, and validation cases only; not a real-world finding.",
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
    parser.add_argument(
        "command",
        choices=("demo", "append-ledger", "verify-ledger", "sync-spine", "verify-spine",\n                 "research-status", "research-reserve", "research-settle"),
    )
    parser.add_argument("--ledger", help="Local append-only JSONL ledger path")
    parser.add_argument("--event-type", choices=sorted(EVENT_TYPES))
    parser.add_argument("--payload-json", default="{}", help="JSON object payload for append-ledger")
    parser.add_argument("--base-url", default=DEFAULT_SPINE_URL, help="Event Spine service root (loopback by default)")
    parser.add_argument("--allow-remote", action="store_true", help="Permit an HTTPS non-loopback Event Spine")
    parser.add_argument("--budget-id", help="Stable research-budget identifier")
    parser.add_argument("--initial-budget", type=float, help="Initial computation/utility budget")
    parser.add_argument("--max-total-credit", type=float, help="Maximum lifetime earned research credit")
    parser.add_argument("--max-credit-per-trial", type=float, help="Maximum research credit per trial")
    parser.add_argument("--family-alpha", type=float, help="Total family-wise error budget across trials")
    parser.add_argument("--credit-rate", type=float, help="Credit-to-budget conversion rate in [0, 1]")
    parser.add_argument("--min-cases", type=int, help="Minimum independent holdout cases before credit is eligible")
    parser.add_argument("--trial-id", help="Stable, idempotent research-trial identifier")
    parser.add_argument("--search-cost", type=float, help="Declared search expenditure in budget units")
    parser.add_argument("--risk-cost", type=float, help="Declared risk cost in budget units")
    parser.add_argument("--records-json", help="JSON array of frozen forecast records, without outcomes")
    parser.add_argument("--samples-json", help="JSON array of frozen forecasts plus held-out outcomes and verifier gates")
    args = parser.parse_args(argv)

    if args.command == "demo":
        print(json.dumps(demo(), indent=2, sort_keys=True, allow_nan=False))
        return 0
    if args.command == "verify-spine":
        result = verify_spine(base_url=args.base_url, allow_remote=args.allow_remote)
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
        return 0 if result.get("valid") else 2
    if not args.ledger:
        parser.error(f"{args.command} requires --ledger PATH")
    store = JsonlLedgerStore(args.ledger)

    research_commands = {"research-status", "research-reserve", "research-settle"}
    if args.command in research_commands:
        policy_values = {
            "--budget-id": args.budget_id,
            "--initial-budget": args.initial_budget,
            "--max-total-credit": args.max_total_credit,
            "--max-credit-per-trial": args.max_credit_per_trial,
            "--family-alpha": args.family_alpha,
            "--credit-rate": args.credit_rate,
            "--min-cases": args.min_cases,
        }
        missing = [name for name, value in policy_values.items() if value is None]
        if missing:
            parser.error(f"{args.command} requires " + ", ".join(missing) + " so the persisted budget policy cannot change implicitly")
        controller = ResearchExperimentController(
            store,
            budget_id=args.budget_id,
            initial_budget=args.initial_budget,
            max_total_credit=args.max_total_credit,
            max_credit_per_trial=args.max_credit_per_trial,
            family_alpha=args.family_alpha,
            credit_rate=args.credit_rate,
            min_cases=args.min_cases,
        )
        if args.command == "research-status":
            result = controller.status()
        elif args.command == "research-reserve":
            if not args.trial_id or not args.records_json or args.search_cost is None:
                parser.error("research-reserve requires --trial-id, --records-json, and --search-cost")
            try:
                with open(args.records_json, "r", encoding="utf-8") as handle:
                    forecast_records = json.load(handle)
            except (OSError, json.JSONDecodeError) as exc:
                parser.error(f"could not read --records-json: {exc}")
            if not isinstance(forecast_records, list):
                parser.error("--records-json must contain a JSON array")
            result = controller.reserve(
                trial_id=args.trial_id,
                forecast_records=forecast_records,
                search_cost=args.search_cost,
                risk_cost=args.risk_cost or 0.0,
            )
        else:
            if not args.trial_id or not args.samples_json:
                parser.error("research-settle requires --trial-id and --samples-json")
            try:
                with open(args.samples_json, "r", encoding="utf-8") as handle:
                    samples = json.load(handle)
            except (OSError, json.JSONDecodeError) as exc:
                parser.error(f"could not read --samples-json: {exc}")
            if not isinstance(samples, list):
                parser.error("--samples-json must contain a JSON array")
            result = controller.settle(trial_id=args.trial_id, samples=samples)
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))
        return 0 if result.get("decision") != "STOP" else 2

    if args.command == "append-ledger":
        if not args.event_type:
            parser.error("append-ledger requires --event-type")
        try:
            payload = json.loads(args.payload_json)
        except json.JSONDecodeError as exc:
            parser.error(f"--payload-json is not valid JSON: {exc}")
        if not isinstance(payload, dict):
            parser.error("--payload-json must be a JSON object")
        event = store.append(args.event_type, payload)
        print(json.dumps(event, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))
        return 0
    if args.command == "verify-ledger":
        ledger = store.load()
        valid, reason = ledger.verify()
        print(json.dumps({"valid": valid, "reason": reason, "replay": ledger.replay()}, indent=2, sort_keys=True, allow_nan=False))
        return 0 if valid else 2
    if args.command == "sync-spine":
        ledger = store.load()
        result = sync_ledger_to_spine(ledger, base_url=args.base_url, allow_remote=args.allow_remote)
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))
        return 0 if result.get("valid") else 2
    parser.error("Unsupported command")
    return 2
