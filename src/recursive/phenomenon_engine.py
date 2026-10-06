"""
EVEZ Phenomenon Engine v0

Dependency-free reference implementation of recursive active measurement with
explicit measurement back-action.

Core law:

    x_(t+1) = F(x_t, a_t, y_t) + B(y_t)
    y_t     = H(x_t, a_t)

The engine also computes a matched counterfactual without measurement input so
that observer influence is an observable quantity rather than a metaphor.

This module does not claim consciousness or truth. It provides an executable
mechanism for controlled perturbation, observation, back-action measurement,
model revision, and recursive experiment selection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import hashlib
import json
import time


Vector = Tuple[float, ...]


def _norm(v: Sequence[float]) -> float:
    return sqrt(sum(x * x for x in v))


def _add(*vectors: Sequence[float]) -> Vector:
    if not vectors:
        return tuple()
    width = len(vectors[0])
    if any(len(v) != width for v in vectors):
        raise ValueError("all vectors must have the same width")
    return tuple(sum(v[i] for v in vectors) for i in range(width))


def _scale(v: Sequence[float], k: float) -> Vector:
    return tuple(k * x for x in v)


def _mean(v: Sequence[float]) -> float:
    return sum(v) / len(v) if v else 0.0


@dataclass(frozen=True)
class PhenomenonState:
    values: Vector
    tick: int = 0


@dataclass(frozen=True)
class Action:
    value: float
    label: str


@dataclass(frozen=True)
class Observation:
    channel: str
    value: float
    back_action: Vector
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class Transition:
    state_before: PhenomenonState
    action: Action
    observation: Observation
    observed_state: PhenomenonState
    counterfactual_state: PhenomenonState
    influence: float
    prediction_error: float
    model_id: str


@dataclass
class LinearHypothesis:
    """Online model: observed value ~= slope * mean(state) + intercept."""

    model_id: str
    slope: float
    intercept: float
    learning_rate: float = 0.05
    error_ema: float = 0.0

    def predict(self, state: PhenomenonState) -> float:
        return self.slope * _mean(state.values) + self.intercept

    def update(self, state: PhenomenonState, observed: float) -> float:
        x = _mean(state.values)
        predicted = self.predict(state)
        error = observed - predicted
        self.slope += self.learning_rate * error * x
        self.intercept += self.learning_rate * error
        self.error_ema = 0.9 * self.error_ema + 0.1 * abs(error)
        return abs(error)


@dataclass
class EngineConfig:
    action_gain: float = 0.10
    observation_gain: float = 0.04
    back_action_gain: float = 0.02
    convergence_epsilon: float = 1e-4
    max_steps: int = 100


class PhenomenonEngine:
    """
    Generate a controlled phenomenon, observe it, let the observation change
    the next state, quantify that change against a matched counterfactual,
    update competing models, and select the next perturbation.
    """

    def __init__(
        self,
        state: PhenomenonState,
        config: Optional[EngineConfig] = None,
        hypotheses: Optional[Iterable[LinearHypothesis]] = None,
    ) -> None:
        self.state = state
        self.config = config or EngineConfig()
        self.hypotheses: List[LinearHypothesis] = list(
            hypotheses
            or (
                LinearHypothesis("M0", 0.50, 0.00),
                LinearHypothesis("M1", 1.00, 0.00),
                LinearHypothesis("M2", 1.50, 0.00),
            )
        )
        if not self.hypotheses:
            raise ValueError("at least one hypothesis is required")
        self.history: List[Transition] = []

    def choose_action(self) -> Action:
        """Choose a bounded perturbation from current model disagreement."""
        x = _mean(self.state.values)
        predictions = [m.predict(self.state) for m in self.hypotheses]
        center = _mean(predictions)
        disagreement = (
            _mean([abs(p - center) for p in predictions])
            if len(predictions) > 1
            else 0.0
        )
        direction = 1.0 if (x + disagreement) >= 0.0 else -1.0
        magnitude = min(1.0, 0.25 + disagreement)
        return Action(direction * magnitude, "DISCRIMINATE")

    def _apply_action(
        self, state: PhenomenonState, action: Action
    ) -> PhenomenonState:
        delta = _scale(
            tuple(1.0 for _ in state.values),
            self.config.action_gain * action.value,
        )
        return PhenomenonState(_add(state.values, delta), state.tick)

    def observe(self, state_after_action: PhenomenonState) -> Observation:
        """
        Measurement has back-action.

        y = H(x)
        b = B(y)

        Replace this method to bind a real sensor, simulator, browser
        observation, device node, or external measurement process.
        """
        y = _mean(state_after_action.values)
        b = _scale(
            tuple(1.0 for _ in state_after_action.values),
            self.config.back_action_gain * y,
        )
        return Observation("mean-state", y, b)

    def _advance(
        self,
        state: PhenomenonState,
        observation: Optional[Observation],
        tick: int,
    ) -> PhenomenonState:
        """Advance once with or without the measurement feedback path."""
        if observation is None:
            observation_delta = tuple(0.0 for _ in state.values)
            back_action = tuple(0.0 for _ in state.values)
        else:
            observation_delta = _scale(
                tuple(1.0 for _ in state.values),
                self.config.observation_gain * observation.value,
            )
            back_action = observation.back_action

        return PhenomenonState(
            _add(state.values, observation_delta, back_action),
            tick,
        )

    def step(self) -> Transition:
        before = self.state

        # 1. Intervene.
        action = self.choose_action()
        after_action = self._apply_action(before, action)

        # 2. Observe. Observation is a causal input, not disposable telemetry.
        observation = self.observe(after_action)

        # 3. Actual branch: measurement changes the state.
        observed_state = self._advance(
            after_action, observation, before.tick + 1
        )

        # 4. Matched counterfactual: same intervention, no measurement path.
        counterfactual_state = self._advance(
            after_action, None, before.tick + 1
        )

        # 5. Quantify observer influence.
        influence = _norm(
            _add(observed_state.values, _scale(counterfactual_state.values, -1.0))
        )

        # 6. Find the currently best explanatory model and update only it.
        predictions = [m.predict(after_action) for m in self.hypotheses]
        winner_index = min(
            range(len(predictions)),
            key=lambda i: abs(observation.value - predictions[i]),
        )
        winner = self.hypotheses[winner_index]
        prediction_error = winner.update(after_action, observation.value)

        transition = Transition(
            state_before=before,
            action=action,
            observation=observation,
            observed_state=observed_state,
            counterfactual_state=counterfactual_state,
            influence=influence,
            prediction_error=prediction_error,
            model_id=winner.model_id,
        )

        self.history.append(transition)
        self.state = observed_state
        return transition

    def run(self, steps: Optional[int] = None) -> List[Transition]:
        limit = self.config.max_steps if steps is None else int(steps)
        if limit < 1:
            raise ValueError("steps must be >= 1")

        result: List[Transition] = []
        for _ in range(limit):
            result.append(self.step())
            if (
                len(result) >= 2
                and abs(result[-1].influence - result[-2].influence)
                < self.config.convergence_epsilon
            ):
                break
        return result

    def snapshot(self) -> Dict[str, object]:
        return {
            "tick": self.state.tick,
            "state": list(self.state.values),
            "history_length": len(self.history),
            "last_measurement_influence": (
                self.history[-1].influence if self.history else None
            ),
            "models": [
                {
                    "id": m.model_id,
                    "slope": m.slope,
                    "intercept": m.intercept,
                    "error_ema": m.error_ema,
                }
                for m in self.hypotheses
            ],
        }

    def hash_snapshot(self) -> str:
        payload = json.dumps(
            self.snapshot(), sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def demo(steps: int = 12) -> Dict[str, object]:
    engine = PhenomenonEngine(
        PhenomenonState((0.20, 0.40, 0.60, 0.80)),
        config=EngineConfig(max_steps=steps),
    )
    transitions = engine.run(steps)
    influences = [t.influence for t in transitions]
    return {
        "steps_executed": len(transitions),
        "final": engine.snapshot(),
        "final_hash": engine.hash_snapshot(),
        "max_influence": max(influences, default=0.0),
        "mean_influence": _mean(influences),
    }


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True))
