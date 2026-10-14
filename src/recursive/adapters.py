"""Adapters that turn external observations into phenomenon-engine measurements.

The engine stays domain-agnostic. Adapters are deliberately small so an
OpenClaw event, browser observation, simulator result, model response, or
device sensor can become an Observation without changing the recursive core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol, Sequence, Tuple


Vector = Tuple[float, ...]


@dataclass(frozen=True)
class Measurement:
    channel: str
    value: float
    metadata: Mapping[str, Any]


class ObservableAdapter(Protocol):
    def measure(self, state: Sequence[float], context: Mapping[str, Any]) -> Measurement:
        ...


@dataclass
class CallableAdapter:
    fn: Callable[[Sequence[float], Mapping[str, Any]], Measurement]

    def measure(self, state: Sequence[float], context: Mapping[str, Any]) -> Measurement:
        return self.fn(state, context)


class EventValueAdapter:
    """Extract a numeric observable from an event-like mapping."""

    def __init__(self, field: str, channel: str | None = None) -> None:
        self.field = field
        self.channel = channel or field

    def measure(self, state: Sequence[float], context: Mapping[str, Any]) -> Measurement:
        if self.field not in context:
            raise KeyError(f"missing observable field: {self.field}")
        value = float(context[self.field])
        return Measurement(self.channel, value, {"source_field": self.field})


class ModelAgreementAdapter:
    """Measure agreement among model predictions supplied in context."""

    def measure(self, state: Sequence[float], context: Mapping[str, Any]) -> Measurement:
        predictions = [float(x) for x in context.get("predictions", ())]
        if not predictions:
            raise ValueError("predictions required")
        mean = sum(predictions) / len(predictions)
        spread = sum(abs(x - mean) for x in predictions) / len(predictions)
        return Measurement("model-disagreement", spread, {"predictions": predictions})


class StateNormAdapter:
    """Simple observable useful for simulations and regression tests."""

    def measure(self, state: Sequence[float], context: Mapping[str, Any]) -> Measurement:
        value = sum(float(x) * float(x) for x in state) ** 0.5
        return Measurement("state-norm", value, {})
