"""Bounded mutation registry."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Any

State = dict[str, Any]
MutationFn = Callable[[State], State]

@dataclass(frozen=True)
class Mutation:
    name: str
    fn: MutationFn
    safety_bound: str
    metadata: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

class MutationRegistry:
    def __init__(self) -> None:
        self._mutations: dict[str, Mutation] = {}

    def register(self, mutation: Mutation) -> None:
        if not mutation.name.strip():
            raise ValueError("mutation name is required")
        if not mutation.safety_bound.strip():
            raise ValueError("mutation safety_bound is required")
        if mutation.name in self._mutations:
            raise ValueError(f"mutation already registered: {mutation.name}")
        self._mutations[mutation.name] = mutation

    def get(self, name: str) -> Mutation:
        mutation = self._mutations.get(name)
        if mutation is None:
            raise KeyError(name)
        if not mutation.enabled:
            raise PermissionError(f"mutation disabled: {name}")
        return mutation

    def names(self) -> list[str]:
        return sorted(self._mutations)

    def apply(self, name: str, state: State) -> State:
        result = self.get(name).fn(dict(state))
        if not isinstance(result, dict):
            raise TypeError("mutation must return a state dict")
        return result

def default_registry() -> MutationRegistry:
    registry = MutationRegistry()
    registry.register(Mutation(
        "inject-unauthorized-action",
        lambda s: {**s, "actual_action": s.get("requested_action")},
        "in-memory synthetic authorization target only",
        {"class": "authority-bypass"},
    ))
    registry.register(Mutation(
        "diverge-recorded-action",
        lambda s: {**s, "recorded_action": "different-from-actual"},
        "in-memory synthetic witness only",
        {"class": "provenance-divergence"},
    ))
    registry.register(Mutation(
        "bounded-noop", lambda s: dict(s),
        "no external side effects", {"class": "control"},
    ))
    return registry
