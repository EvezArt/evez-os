"""Decision-theoretic research allocation: search only when expected value justifies cost."""
from __future__ import annotations

import math
from typing import Any, Iterable, Mapping


def _probabilities(values: Mapping[str, float]) -> dict[str, float]:
    if not values:
        raise ValueError("At least one hypothesis is required")
    if any(not math.isfinite(float(value)) or float(value) < 0 for value in values.values()):
        raise ValueError("Probabilities must be finite and non-negative")
    total = math.fsum(float(value) for value in values.values())
    if total <= 0:
        raise ValueError("Probabilities sum to zero")
    return {key: float(value) / total for key, value in sorted(values.items())}


def _validate_outcomes(prior: Mapping[str, float], outcomes: Mapping[str, Any]) -> dict[str, float]:
    p = _probabilities(prior)
    if not isinstance(outcomes, Mapping) or not outcomes:
        raise ValueError("A test must define at least one possible outcome")
    for outcome, row in outcomes.items():
        if not isinstance(row, Mapping) or set(row) != set(p):
            raise ValueError(f"Outcome {outcome!r} must define likelihoods for every hypothesis")
    for hypothesis in p:
        likelihoods = [float(outcomes[outcome][hypothesis]) for outcome in outcomes]
        if any(not math.isfinite(x) or x < 0 or x > 1 for x in likelihoods):
            raise ValueError("Outcome likelihoods must be finite values in [0, 1]")
        total = math.fsum(likelihoods)
        if not math.isclose(total, 1.0, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError(f"Outcome likelihoods for {hypothesis} sum to {total}, not 1")
    return p


def _best_expected_utility(
    probabilities: Mapping[str, float],
    action_utilities: Mapping[str, Mapping[str, float]],
) -> tuple[float, str]:
    if not action_utilities:
        raise ValueError("At least one available action is required")
    hypotheses = set(probabilities)
    scored = []
    for action, utilities in action_utilities.items():
        if set(utilities) != hypotheses:
            raise ValueError(f"Action {action!r} must define utility for every hypothesis")
        vals = [float(utilities[h]) for h in probabilities]
        if any(not math.isfinite(v) for v in vals):
            raise ValueError("Action utilities must be finite")
        scored.append((math.fsum(probabilities[h] * float(utilities[h]) for h in probabilities), str(action)))
    # Stable tie-breaking by action identifier makes replay deterministic.
    return sorted(scored, key=lambda pair: (-pair[0], pair[1]))[0]


def expected_value_of_sample_information(
    prior: Mapping[str, float],
    test: Mapping[str, Any],
    action_utilities: Mapping[str, Mapping[str, float]],
) -> dict[str, Any]:
    """EVSI = expected best utility after a test minus best utility before it.

    Unlike entropy reduction, EVSI measures whether information can improve an
    actual downstream decision. Utilities must be defined in the same units as
    test cost and risk after weighting. Test outcome likelihoods are P(outcome|H).
    """
    outcomes = test.get("outcomes")
    p = _validate_outcomes(prior, outcomes)
    before_value, before_action = _best_expected_utility(p, action_utilities)
    expected_after = 0.0
    outcome_details = []
    for outcome, likelihoods in outcomes.items():
        p_outcome = math.fsum(p[h] * float(likelihoods[h]) for h in p)
        if p_outcome <= 0:
            continue
        posterior = _probabilities({h: p[h] * float(likelihoods[h]) for h in p})
        after_value, after_action = _best_expected_utility(posterior, action_utilities)
        expected_after += p_outcome * after_value
        outcome_details.append({
            "outcome": str(outcome),
            "probability": p_outcome,
            "posterior": posterior,
            "best_action": after_action,
            "best_expected_utility": after_value,
        })
    evsi = expected_after - before_value
    if evsi < -1e-8:
        raise ArithmeticError("EVSI is negative; inspect utility/outcome model")
    return {
        "expected_value_of_sample_information": max(0.0, evsi),
        "best_action_before_test": before_action,
        "best_expected_utility_before_test": before_value,
        "expected_best_utility_after_test": expected_after,
        "outcomes": outcome_details,
    }


def rank_decision_tests(
    prior: Mapping[str, float],
    tests: Iterable[Mapping[str, Any]],
    action_utilities: Mapping[str, Mapping[str, float]],
    *,
    cost_weight: float = 1.0,
    risk_weight: float = 1.0,
) -> list[dict[str, Any]]:
    """Rank explicitly permitted tests by EVSI minus weighted cost and risk.

    Cost and risk must already be expressed in units compatible with the action
    utilities. A positive score does not itself authorize a test.
    """
    if not math.isfinite(cost_weight) or not math.isfinite(risk_weight) or cost_weight < 0 or risk_weight < 0:
        raise ValueError("Cost and risk weights must be finite and non-negative")
    rows = []
    for test in tests:
        if test.get("permitted") is not True:
            continue
        result = expected_value_of_sample_information(prior, test, action_utilities)
        cost, risk = float(test.get("cost", 0.0)), float(test.get("risk", 0.0))
        if any(not math.isfinite(x) or x < 0 for x in (cost, risk)):
            raise ValueError("Test cost and risk must be finite and non-negative")
        evsi = result["expected_value_of_sample_information"]
        rows.append({
            "id": str(test.get("id", "")),
            "evsi": evsi,
            "cost": cost,
            "risk": risk,
            "net_value": evsi - cost_weight * cost - risk_weight * risk,
            "diagnostics": result,
        })
    return sorted(rows, key=lambda row: (-row["net_value"], -row["evsi"], row["id"]))


def choose_next_test(
    prior: Mapping[str, float],
    tests: Iterable[Mapping[str, Any]],
    action_utilities: Mapping[str, Mapping[str, float]],
    *,
    remaining_budget: float,
    steps_completed: int,
    max_steps: int,
    minimum_net_value: float = 0.0,
    cost_weight: float = 1.0,
    risk_weight: float = 1.0,
) -> dict[str, Any]:
    """Finite research gate: choose a high-value permissible test or stop."""
    if not math.isfinite(remaining_budget) or remaining_budget < 0:
        raise ValueError("remaining_budget must be finite and non-negative")
    if not math.isfinite(minimum_net_value):
        raise ValueError("minimum_net_value must be finite")
    if steps_completed < 0 or max_steps < 0:
        raise ValueError("step limits must be non-negative")
    if steps_completed >= max_steps:
        return {"decision": "STOP", "reason": "MAX_STEPS_REACHED", "selected_test": None}
    if remaining_budget <= 0:
        return {"decision": "STOP", "reason": "BUDGET_EXHAUSTED", "selected_test": None}
    ranked = rank_decision_tests(prior, tests, action_utilities,
                                 cost_weight=cost_weight, risk_weight=risk_weight)
    affordable = [row for row in ranked if row["cost"] <= remaining_budget]
    if not affordable:
        return {"decision": "STOP", "reason": "NO_PERMITTED_AFFORDABLE_TEST", "selected_test": None, "ranking": ranked}
    best = affordable[0]
    if best["net_value"] <= minimum_net_value:
        return {"decision": "STOP", "reason": "MARGINAL_VALUE_NOT_ABOVE_THRESHOLD", "selected_test": None, "ranking": ranked}
    return {"decision": "CONTINUE", "reason": "POSITIVE_EXPECTED_NET_VALUE", "selected_test": best, "ranking": ranked}


def prequential_log_score(
    forecast: Mapping[str, float],
    observed_outcome: str,
    *,
    probability_floor: float = 1e-12,
) -> float:
    """Capped logarithmic score for an outcome not used to fit the forecast.

    Higher is better. The probability floor prevents a zero-probability model
    from producing negative infinity, but it must be kept fixed across runs.
    """
    p = _probabilities(forecast)
    if observed_outcome not in p:
        raise ValueError("Observed outcome is absent from the forecast outcome space")
    if not math.isfinite(probability_floor) or not 0 < probability_floor < 1:
        raise ValueError("probability_floor must be finite and in (0, 1)")
    return math.log(max(p[observed_outcome], probability_floor))


def realized_research_reward(
    baseline_forecast: Mapping[str, float],
    updated_forecast: Mapping[str, float],
    observed_outcome: str,
    *,
    search_cost: float,
    risk_cost: float,
    verifier_accepted: bool,
    source_independence_verified: bool,
    source_is_duplicate: bool,
    prediction_frozen_before_outcome: bool,
    outcome_held_out: bool,
    score_weight: float = 1.0,
    probability_floor: float = 1e-12,
) -> dict[str, Any]:
    """Score realized research only against an independently verified holdout.

    Reward = score_weight * (updated log score - baseline log score)
             - search cost - risk cost.
    If evidence is unverified, derivative, or leaked into model fitting, no
    positive research reward is permitted; expenditure remains a cost.
    """
    numeric = (search_cost, risk_cost, score_weight)
    if any(not math.isfinite(x) or x < 0 for x in numeric):
        raise ValueError("Costs and score_weight must be finite and non-negative")
    gates = {
        "verifier_accepted": verifier_accepted is True,
        "source_independence_verified": source_independence_verified is True,
        "source_is_not_duplicate": source_is_duplicate is False,
        "prediction_frozen_before_outcome": prediction_frozen_before_outcome is True,
        "outcome_held_out": outcome_held_out is True,
    }
    expenditure = search_cost + risk_cost
    failed = [name for name, passed in gates.items() if not passed]
    if failed:
        return {
            "eligible": False,
            "failed_gates": failed,
            "baseline_log_score": None,
            "updated_log_score": None,
            "score_delta": None,
            "gross_reward": 0.0,
            "search_cost": search_cost,
            "risk_cost": risk_cost,
            # Round to 12dp: 0.1+0.2 is 0.30000000000000004 in IEEE-754 and
            # every reward comparison downstream (net_reward > 0, etc.)
            # must behave identically on any platform.
            "net_reward": round(-expenditure, 12),
        }
    if set(baseline_forecast) != set(updated_forecast):
        raise ValueError("Baseline and updated forecasts must use the same outcome space")
    before = prequential_log_score(baseline_forecast, observed_outcome, probability_floor=probability_floor)
    after = prequential_log_score(updated_forecast, observed_outcome, probability_floor=probability_floor)
    delta = after - before
    gross = score_weight * delta
    return {
        "eligible": True,
        "failed_gates": [],
        "baseline_log_score": before,
        "updated_log_score": after,
        "score_delta": delta,
        "gross_reward": gross,
        "search_cost": search_cost,
        "risk_cost": risk_cost,
        "net_reward": gross - expenditure,
    }


def _strict_forecast_distribution(forecast: Mapping[str, float]) -> dict[str, float]:
    """Validate a forecast distribution without silently repairing its sum."""
    if not isinstance(forecast, Mapping) or not forecast:
        raise ValueError("Forecast must be a non-empty outcome-probability mapping")
    result = {}
    for outcome, raw in forecast.items():
        if not isinstance(outcome, str) or not outcome:
            raise ValueError("Forecast outcome identifiers must be non-empty strings")
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise ValueError("Forecast probabilities must be numeric, not booleans")
        value = float(raw)
        if not math.isfinite(value) or value < 0 or value > 1:
            raise ValueError("Forecast probabilities must be finite and in [0, 1]")
        result[outcome] = value
    total = math.fsum(result.values())
    if not math.isclose(total, 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(f"Forecast probabilities sum to {total}, not 1")
    return dict(sorted(result.items()))


def negative_brier_score(forecast: Mapping[str, float], observed_outcome: str) -> float:
    """Bounded strictly proper categorical score; higher is better, range [-2, 0]."""
    p = _strict_forecast_distribution(forecast)
    if observed_outcome not in p:
        raise ValueError("Observed outcome is absent from the forecast outcome space")
    return -math.fsum((probability - (1.0 if outcome == observed_outcome else 0.0)) ** 2
                      for outcome, probability in p.items())


def aggregate_research_reward(
    samples: Iterable[Mapping[str, Any]],
    *,
    search_cost: float,
    risk_cost: float,
    projected_future_cases: float = 1.0,
    score_weight: float = 1.0,
    min_cases: int = 30,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """Reward an investigation only when its held-out Brier-score gain clears a bound.

    Each sample must be a distinct independent evaluation unit, with baseline and
    updated forecasts frozen before the outcome. The paired negative-Brier score
    delta lies in [-2, 2], so Hoeffding gives a conservative one-sided lower
    confidence bound: mean_delta - 4*sqrt(log(1/alpha)/(2*n)).
    Extrapolation is explicit via projected_future_cases. Costs are paid even
    when evidence gates fail; unverified/duplicate/leaked samples cannot earn
    positive reward. This function does not prove sample independence: the
    caller/verifier must establish the declared gates.
    """
    scalars = (search_cost, risk_cost, projected_future_cases, score_weight, alpha)
    if any(not math.isfinite(x) for x in scalars):
        raise ValueError("Reward parameters must be finite")
    if search_cost < 0 or risk_cost < 0 or projected_future_cases < 0 or score_weight < 0:
        raise ValueError("Costs, projection, and score weight must be non-negative")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between 0 and 1")
    if isinstance(min_cases, bool) or not isinstance(min_cases, int) or min_cases < 2:
        raise ValueError("min_cases must be an integer >= 2")

    rows = list(samples)
    expenditure = search_cost + risk_cost
    if len(rows) < min_cases:
        return {
            "status": "NO_REWARD_INSUFFICIENT_HOLDOUT",
            "eligible": False,
            "n_cases": len(rows),
            "min_cases": min_cases,
            "failed_gates": [],
            "mean_score_delta": None,
            "lower_confidence_bound": None,
            "confidence_level": 1 - alpha,
            "gross_reward": 0.0,
            "search_cost": search_cost,
            "risk_cost": risk_cost,
            "net_reward": -expenditure,
        }

    seen_ids, seen_units = set(), set()
    failed_gates = []
    deltas = []
    for index, sample in enumerate(rows):
        sample_id = sample.get("id")
        unit = sample.get("independence_key")
        if not isinstance(sample_id, str) or not sample_id:
            raise ValueError(f"Sample {index} requires a non-empty id")
        if sample_id in seen_ids:
            raise ValueError(f"Duplicate sample id: {sample_id}")
        seen_ids.add(sample_id)
        if not isinstance(unit, str) or not unit:
            raise ValueError(f"Sample {sample_id} requires an independence_key")
        if unit in seen_units:
            raise ValueError(f"Repeated independence_key {unit!r}; evaluation units are not distinct")
        seen_units.add(unit)

        gates = {
            "verifier_accepted": sample.get("verifier_accepted") is True,
            "source_independence_verified": sample.get("source_independence_verified") is True,
            "source_is_not_duplicate": sample.get("source_is_duplicate") is False,
            "prediction_frozen_before_outcome": sample.get("prediction_frozen_before_outcome") is True,
            "outcome_held_out": sample.get("outcome_held_out") is True,
        }
        failed_gates.extend(f"{sample_id}:{name}" for name, passed in gates.items() if not passed)
        baseline = _strict_forecast_distribution(sample.get("baseline_forecast"))
        updated = _strict_forecast_distribution(sample.get("updated_forecast"))
        if set(baseline) != set(updated):
            raise ValueError(f"Sample {sample_id}: baseline and updated outcome spaces differ")
        outcome = sample.get("observed_outcome")
        if outcome not in baseline:
            raise ValueError(f"Sample {sample_id}: outcome absent from forecast distribution")
        deltas.append(
            negative_brier_score(updated, outcome) -
            negative_brier_score(baseline, outcome)
        )

    if failed_gates:
        return {
            "status": "NO_REWARD_FAILED_EVIDENCE_GATES",
            "eligible": False,
            "n_cases": len(rows),
            "min_cases": min_cases,
            "failed_gates": failed_gates,
            "mean_score_delta": None,
            "lower_confidence_bound": None,
            "confidence_level": 1 - alpha,
            "gross_reward": 0.0,
            "search_cost": search_cost,
            "risk_cost": risk_cost,
            "net_reward": -expenditure,
        }

    n = len(deltas)
    mean_delta = math.fsum(deltas) / n
    radius = 4.0 * math.sqrt(math.log(1.0 / alpha) / (2.0 * n))
    lower_bound = mean_delta - radius
    gross_reward = projected_future_cases * score_weight * max(0.0, lower_bound)
    net_reward = gross_reward - expenditure
    rewardable = lower_bound > 0 and net_reward > 0
    return {
        "status": "REWARD_SUPPORTED" if rewardable else "NO_REWARD_GAIN_NOT_PROVEN",
        "eligible": True,
        "rewardable": rewardable,
        "n_cases": n,
        "min_cases": min_cases,
        "failed_gates": [],
        "score": "negative_categorical_brier",
        "mean_score_delta": mean_delta,
        "confidence_radius": radius,
        "lower_confidence_bound": lower_bound,
        "confidence_level": 1 - alpha,
        "projected_future_cases": projected_future_cases,
        "score_weight": score_weight,
        "gross_reward": gross_reward,
        "search_cost": search_cost,
        "risk_cost": risk_cost,
        "net_reward": net_reward,
    }
