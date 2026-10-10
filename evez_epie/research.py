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
    return max(scored, key=lambda pair: (pair[0], tuple(-ord(c) for c in pair[1])))


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
