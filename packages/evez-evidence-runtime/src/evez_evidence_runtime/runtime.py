"""Executable evidence/adversarial runtime."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .compiler import ClaimCompiler, TestPlan
from .invariants import InvariantBattery, InvariantResult
from .observer import Observation, observe
from .registry import MutationRegistry, default_registry
from .rollback import RollbackController
from .recovery import FailureClass, RecoveryAlternative, RecoveryCoordinator, RecoveryReceipt, RecoveryWitness
from .spine import EvidenceSpine
from .surface import FailureSurface, SurfaceMapper
from .threat import ThreatEngine

@dataclass(frozen=True)
class RuntimeResult:
    run_id: str
    classification: str
    claim: str
    test_plan: dict[str, Any]
    threat_case: dict[str, Any]
    observation: dict[str, Any]
    invariants: list[dict[str, Any]]
    rollback: dict[str, Any]
    receipt: dict[str, Any]

class EvidenceRuntime:
    def __init__(self, *, spine: EvidenceSpine, mapper: SurfaceMapper | None = None, threats: ThreatEngine | None = None, mutations: MutationRegistry | None = None, rollback: RollbackController | None = None) -> None:
        self.spine = spine
        self.mapper = mapper or SurfaceMapper()
        self.threats = threats or ThreatEngine()
        self.mutations = mutations or default_registry()
        self.rollback_controller = rollback or RollbackController()
        self.compiler = ClaimCompiler()
        self.recovery = RecoveryCoordinator(spine=spine)

    def plan_recovery(
        self,
        *,
        failure_id: str,
        failure_class: FailureClass,
        alternatives: list[RecoveryAlternative] | None = None,
        allow_human: bool = False,
    ) -> RecoveryWitness:
        """Create an evidence-backed recovery plan without executing the action."""
        return self.recovery.plan(
            failure_id=failure_id,
            failure_class=failure_class,
            alternatives=alternatives,
            allow_human=allow_human,
        )

    def begin_recovery(self, *, witness: RecoveryWitness) -> bool:
        """Consume a bounded recovery attempt and witness the authorization gate."""
        return self.recovery.attempt(witness=witness)

    def observe_recovery(
        self,
        *,
        witness: RecoveryWitness,
        expected: bool,
        observed: bool,
        contradictory: bool = False,
        observation: str = "",
    ) -> RecoveryReceipt:
        """Classify recovery evidence without promoting a broader claim."""
        return self.recovery.observe(
            witness=witness,
            expected=expected,
            observed=observed,
            contradictory=contradictory,
            observation=observation,
        )

    def run(self, *, run_id: str, claim: str, surface: FailureSurface, mutation_name: str, target_state: dict[str, Any], invariant_battery: InvariantBattery, required_evidence: list[str] | None = None) -> RuntimeResult:
        plan: TestPlan = self.compiler.compile(claim, observables=list(surface.observables), required_evidence=list(required_evidence or surface.observables))
        threat_case = next((t for t in self.threats.generate(surface) if t.mutation_name == mutation_name), None)
        if threat_case is None:
            raise ValueError(f"mutation is not authorized for surface: {mutation_name}")

        before = dict(target_state)
        snapshot = self.rollback_controller.snapshot(before)
        self.spine.append("run_start", {"run_id": run_id, "claim": claim, "surface": surface.to_dict()})

        try:
            after = self.mutations.apply(mutation_name, before)
            observation: Observation = observe(before, after)
            inv_results: list[InvariantResult] = invariant_battery.check(after)
            rollback_result = self.rollback_controller.rollback(snapshot, after)
            all_hold = invariant_battery.all_hold(inv_results)

            if not rollback_result.verified:
                classification = "CONTRADICTION"
            elif not all_hold:
                classification = "VIOLATION"
            elif observation.delta:
                classification = "PASS"
            else:
                classification = "UNKNOWN"

            receipt_payload = {
                "run_id": run_id,
                "parent_event_hash": self.spine.last_hash,
                "target": {"kind": "synthetic", "state_hash_before": observation.before_hash, "state_hash_after": observation.after_hash},
                "surface": surface.to_dict(),
                "mutation": {"name": mutation_name, "safety_bound": threat_case.safety_bound},
                "before": observation.before,
                "action": mutation_name,
                "after": observation.after,
                "delta": observation.delta,
                "invariants": {"checked": [r.name for r in inv_results], "failed": [r.name for r in inv_results if not r.passed]},
                "rollback": {"attempted": rollback_result.attempted, "verified": rollback_result.verified},
                "classification": classification,
                "evidence": {"test_executed": True, "external_side_effects": False, "claim_status": "tested-but-not-proven"},
            }
            event = self.spine.append("evidence_receipt", receipt_payload)
            receipt_payload["event_hash"] = event["event_hash"]
            return RuntimeResult(
                run_id, classification, claim, plan.to_dict(), threat_case.to_dict(),
                {"before": observation.before, "after": observation.after, "delta": observation.delta},
                [r.__dict__ for r in inv_results], rollback_result.__dict__, receipt_payload,
            )
        except Exception as exc:
            self.spine.append("run_error", {"run_id": run_id, "error": str(exc)})
            raise
