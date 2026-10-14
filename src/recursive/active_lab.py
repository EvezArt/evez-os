"""
High-level orchestration for the recursive phenomenon loop.

The lab keeps three concerns separate:
1. PhenomenonEngine generates and measures local experiments.
2. ArmorCharmer decides whether an intended side effect is permitted.
3. ExperimentRecord provides deterministic provenance.

That separation makes the recursive loop composable with OpenClaw without
giving the core engine authority over browsers, deployments, secrets, money,
or other external effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .armor_charmer import ArmorCharmer, GateDecision, ProposedAction, RiskClass
from .experiment_protocol import ExperimentRecord, chain
from .falsification import FalsificationRule, should_falsify
from .phenomenon_engine import PhenomenonEngine, Transition


@dataclass(frozen=True)
class LabStep:
    transition: Transition
    record: ExperimentRecord
    gate: GateDecision
    falsified: bool


class ActiveMeasurementLab:
    """
    Safe orchestration surface around PhenomenonEngine.

    Local simulation is intentionally the default. External actions must be
    authorized separately through ArmorCharmer before an external executor is
    invoked.
    """

    def __init__(
        self,
        engine: PhenomenonEngine,
        *,
        run_id: str = "run-0",
        armor: ArmorCharmer | None = None,
        falsification_rules: Iterable[FalsificationRule] = (),
    ) -> None:
        self.engine = engine
        self.run_id = run_id
        self.armor = armor or ArmorCharmer()
        self.rules = tuple(falsification_rules)
        self._records: list[ExperimentRecord] = []
        self._steps: list[LabStep] = []

    def authorize_external(
        self,
        action: ProposedAction,
        context: Mapping[str, object] | None = None,
    ) -> GateDecision:
        """Check an external action without executing it."""
        return self.armor.authorize(action, context)

    def step(self) -> LabStep:
        intended = ProposedAction(
            label="phenomenon-engine-step",
            risk=RiskClass.SIMULATE,
            reversible=True,
            side_effect=False,
            scope="local",
            rationale="advance the causal measurement simulation",
        )
        gate = self.armor.authorize(intended)
        if not gate.allowed:
            raise PermissionError(gate.reason)

        transition = self.engine.step()
        record = ExperimentRecord(
            run_id=self.run_id,
            tick=transition.observed_state.tick,
            state_before=transition.state_before.values,
            action_label=transition.action.label,
            action_value=transition.action.value,
            observable_channel=transition.observation.channel,
            observable_value=transition.observation.value,
            observed_state=transition.observed_state.values,
            counterfactual_state=transition.counterfactual_state.values,
            measurement_influence=transition.influence,
            prediction_error=transition.prediction_error,
            selected_model=transition.model_id,
        )
        falsified = should_falsify(
            self.rules,
            transition.model_id,
            transition.prediction_error,
        )
        self._steps.append(LabStep(transition, record, gate, falsified))
        self._records.append(record)
        return self._steps[-1]

    def run(self, steps: int = 1) -> list[LabStep]:
        if steps < 1:
            raise ValueError("steps must be >= 1")
        return [self.step() for _ in range(steps)]

    @property
    def steps(self) -> tuple[LabStep, ...]:
        return tuple(self._steps)

    @property
    def records(self) -> tuple[ExperimentRecord, ...]:
        return tuple(chain(self._records))

    def event_stream(self) -> list[dict]:
        return [dict(record.as_event()) for record in self.records]
