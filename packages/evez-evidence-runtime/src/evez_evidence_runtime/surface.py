"""Failure-surface mapping.

A surface is not a vulnerability claim. It is a statement of where authority,
data, execution, or observation crosses a boundary and what can be measured there.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Iterable

@dataclass(frozen=True)
class FailureSurface:
    name: str
    boundary: str
    preconditions: tuple[str, ...]
    observables: tuple[str, ...]
    risk_class: str = "synthetic"

    def to_dict(self) -> dict:
        return asdict(self)

class SurfaceMapper:
    def map_surface(self, *, name: str, boundary: str, preconditions: Iterable[str] = (), observables: Iterable[str] = (), risk_class: str = "synthetic") -> FailureSurface:
        surface = FailureSurface(name, boundary, tuple(preconditions), tuple(observables), risk_class)
        if not surface.name.strip() or not surface.boundary.strip():
            raise ValueError("surface name and boundary are required")
        if not surface.observables:
            raise ValueError("a surface needs at least one observable")
        return surface

    def default_tool_authorization_surface(self) -> FailureSurface:
        return self.map_surface(
            name="tool-authorization",
            boundary="tool request -> policy gate -> execution -> witness",
            preconditions=("requested_action is declared", "authorized_action is declared"),
            observables=("requested_action", "authorized_action", "actual_action", "recorded_action"),
            risk_class="authority",
        )
