"""
Falsification layer for recursive active measurement.

The goal is not to find the prettiest model. It is to choose observations
that can separate competing models and to record the conditions under which a
hypothesis should be rejected.

This module is deterministic and side-effect free.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import fsum
from typing import Callable, Iterable, Sequence, Tuple


Vector = Tuple[float, ...]


@dataclass(frozen=True)
class HypothesisView:
    model_id: str
    predict: Callable[[Sequence[float], float], float]


@dataclass(frozen=True)
class ExperimentCandidate:
    action_value: float
    action_label: str
    predicted_values: Tuple[float, ...]
    disagreement: float
    cost: float

    @property
    def discrimination_score(self) -> float:
        return self.disagreement - self.cost


@dataclass(frozen=True)
class FalsificationRule:
    model_id: str
    max_abs_error: float

    def reject(self, prediction_error: float) -> bool:
        return abs(float(prediction_error)) > self.max_abs_error


def _mean(values: Sequence[float]) -> float:
    return fsum(values) / len(values) if values else 0.0


def _spread(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    center = _mean(values)
    return _mean([abs(v - center) for v in values])


def rank_candidates(
    state: Sequence[float],
    hypotheses: Iterable[HypothesisView],
    action_values: Iterable[float],
    *,
    cost_fn: Callable[[float], float] | None = None,
) -> list[ExperimentCandidate]:
    """Return candidate interventions from most to least discriminating."""
    models = tuple(hypotheses)
    costs = cost_fn or (lambda _: 0.0)
    candidates: list[ExperimentCandidate] = []

    for action_value in action_values:
        predictions = tuple(
            float(model.predict(state, float(action_value))) for model in models
        )
        cost = max(0.0, float(costs(float(action_value))))
        candidates.append(
            ExperimentCandidate(
                action_value=float(action_value),
                action_label="DISCRIMINATE",
                predicted_values=predictions,
                disagreement=_spread(predictions),
                cost=cost,
            )
        )

    return sorted(
        candidates,
        key=lambda candidate: (
            candidate.discrimination_score,
            candidate.disagreement,
            -candidate.cost,
        ),
        reverse=True,
    )


def should_falsify(
    rules: Iterable[FalsificationRule],
    model_id: str,
    prediction_error: float,
) -> bool:
    """Return True when the selected model has crossed its rejection bound."""
    for rule in rules:
        if rule.model_id == model_id:
            return rule.reject(prediction_error)
    return False
