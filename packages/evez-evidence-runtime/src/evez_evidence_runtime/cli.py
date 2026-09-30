"""Command-line self-audit and epistemic optimization demos."""
from __future__ import annotations
import argparse
import json
import tempfile
from .dependencies import DependencyGraph
from .invariants import authorization_battery
from .optimizer import CandidateTest, TestSelector
from .recovery import FailureClass, RecoveryAlternative, RecoveryEngine
from .runtime import EvidenceRuntime
from .spine import EvidenceSpine
from .surface import SurfaceMapper
from .self_audit import SelfAuditor

def run_demo() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        spine = EvidenceSpine(f"{tmp}/chain.jsonl")
        result = EvidenceRuntime(spine=spine).run(
            run_id="self-audit-authority-conflict",
            claim="Tool authorization cannot be bypassed.",
            surface=SurfaceMapper().default_tool_authorization_surface(),
            mutation_name="inject-unauthorized-action",
            target_state={
                "requested_action": "delete_synthetic_record",
                "authorized_action": "read_synthetic_record",
                "actual_action": "read_synthetic_record",
                "recorded_action": "read_synthetic_record",
            },
            invariant_battery=authorization_battery(),
        )
        return {
            "result": result.__dict__,
            "spine_verify": spine.verify(),
            "self_audit": SelfAuditor().audit(spine).__dict__,
            "optimization": run_optimization_demo(),
        }

def run_optimization_demo() -> dict:
    graph = DependencyGraph()
    graph.depends_on("authorization_claim", "authorization_assumption")
    graph.depends_on("runtime_model", "authorization_claim")

    candidates = [
        CandidateTest(
            "direct_boundary_probe",
            "Probe the authorization boundary with a synthetic conflict.",
            information_gain=5.0,
            contradiction_resolution=5.0,
            reproducibility=1.0,
            cost=1.0,
            risk=0.0,
            discriminates=True,
            observable=True,
            safe=True,
            affects_claim=True,
            dependencies=frozenset({"authorization_assumption"}),
            falsifiers=frozenset({"unauthorized_execution"}),
        ),
        CandidateTest(
            "expensive_nondiscriminating",
            "Expensive test that cannot distinguish the competing hypotheses.",
            information_gain=9.0,
            contradiction_resolution=0.0,
            reproducibility=1.0,
            cost=100.0,
            risk=0.2,
            discriminates=False,
            observable=True,
            safe=True,
            affects_claim=True,
        ),
        CandidateTest(
            "unsafe_external_mutation",
            "External mutation deliberately outside the runtime safety boundary.",
            information_gain=100.0,
            contradiction_resolution=100.0,
            reproducibility=1.0,
            cost=1.0,
            risk=100.0,
            discriminates=True,
            observable=True,
            safe=False,
            affects_claim=True,
        ),
    ]
    decision = TestSelector(max_risk=1.0).select(
        candidates,
        graph=graph,
        uncertain={"authorization_assumption"},
    )
    return {
        "selected": decision.selected,
        "ranked": list(decision.ranked),
        "rejected": decision.rejected,
        "bottlenecks": list(decision.bottlenecks),
        "saturation": decision.saturation,
        "rationale": list(decision.rationale),
    }


def run_recovery_demo() -> dict:
    engine = RecoveryEngine()
    alternatives = [
        RecoveryAlternative(
            action_id="bounded-idempotent-retry",
            description="Retry a synthetic transient dependency operation once.",
            failure_classes=frozenset({FailureClass.TRANSIENT}),
            safe=True, authorized=True, observable=True, reversible=True,
            idempotent=True, compensatable=False, cost=1.0, risk=0.1,
            information_gain=3.0, blast_radius=0.1, retryable=True,
            expected_observation="dependency responds",
        ),
        RecoveryAlternative(
            action_id="unauthorized-external-mutation",
            description="External mutation outside the runtime boundary.",
            failure_classes=frozenset({FailureClass.TRANSIENT}),
            safe=False, authorized=False, observable=True, reversible=False,
            idempotent=False, compensatable=False, cost=1.0, risk=10.0,
            information_gain=100.0, blast_radius=10.0,
        ),
    ]
    d = engine.plan(failure_id="demo-transient", failure_class=FailureClass.TRANSIENT, alternatives=alternatives)
    return {"selected": d.selected, "ranked": list(d.ranked), "rejected": d.rejected, "state": d.state.value, "rationale": list(d.rationale)}

def main() -> None:
    parser = argparse.ArgumentParser(description="EVEZ Evidence Runtime")
    parser.add_argument(
        "command",
        nargs="?",
        default="self-audit",
        choices=["self-audit", "optimize", "recover"],
    )
    args = parser.parse_args()
    output = run_demo() if args.command == "self-audit" else (run_optimization_demo() if args.command == "optimize" else run_recovery_demo())
    print(json.dumps(output, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
