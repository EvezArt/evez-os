"""
Armor Charmer: a deterministic boundary for recursive experiments.

The name is intentionally playful. The behavior is not.

This module separates:
- what an experiment wants to do,
- what side effects it could cause,
- what capability has been explicitly granted,
- whether the action is reversible,
- whether human authorization is required.

Default posture is fail-closed. Simulation and pure observation are allowed.
External, sensitive, or irreversible actions require an explicit capability.
No credentials, network clients, or execution backends live here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet, Mapping


class RiskClass(str, Enum):
    OBSERVE = "observe"
    SIMULATE = "simulate"
    REVERSIBLE = "reversible"
    EXTERNAL = "external"
    SENSITIVE = "sensitive"
    IRREVERSIBLE = "irreversible"


@dataclass(frozen=True)
class ProposedAction:
    label: str
    risk: RiskClass = RiskClass.SIMULATE
    reversible: bool = True
    side_effect: bool = False
    scope: str = "local"
    rationale: str = ""


@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    reason: str
    risk: RiskClass
    requires_human: bool
    capability: str | None = None


@dataclass(frozen=True)
class ArmorCharmer:
    """
    Policy-only gate. It does not execute actions.

    capabilities contains explicit grants such as:
      "external:browser"
      "sensitive:data"
      "irreversible:deploy"

    A capability is necessary but not sufficient for an irreversible action:
    those actions always retain a human-authorization requirement.
    """

    capabilities: FrozenSet[str] = frozenset()

    def authorize(
        self,
        action: ProposedAction,
        context: Mapping[str, object] | None = None,
    ) -> GateDecision:
        context = context or {}

        if not action.label.strip():
            return GateDecision(False, "action label is required", action.risk, False)

        if action.risk in {RiskClass.OBSERVE, RiskClass.SIMULATE}:
            if action.side_effect:
                return GateDecision(
                    False,
                    "observation/simulation cannot declare an external side effect",
                    action.risk,
                    False,
                )
            return GateDecision(True, "safe local experiment", action.risk, False)

        required = f"{action.risk.value}:{action.scope}"

        if required not in self.capabilities:
            return GateDecision(
                False,
                f"missing explicit capability: {required}",
                action.risk,
                action.risk in {RiskClass.SENSITIVE, RiskClass.IRREVERSIBLE},
                required,
            )

        if action.risk == RiskClass.REVERSIBLE and not action.reversible:
            return GateDecision(
                False,
                "reversible risk class requires reversible=True",
                action.risk,
                False,
                required,
            )

        if action.risk == RiskClass.EXTERNAL and not action.side_effect:
            return GateDecision(
                False,
                "external risk class requires side_effect=True",
                action.risk,
                False,
                required,
            )

        if action.risk in {RiskClass.SENSITIVE, RiskClass.IRREVERSIBLE}:
            human = bool(context.get("human_authorized", False))
            if not human:
                return GateDecision(
                    False,
                    "explicit human authorization required",
                    action.risk,
                    True,
                    required,
                )

        return GateDecision(
            True,
            "explicit capability and policy checks satisfied",
            action.risk,
            action.risk in {RiskClass.SENSITIVE, RiskClass.IRREVERSIBLE},
            required,
        )
