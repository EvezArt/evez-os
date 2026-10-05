import unittest

from mobile.evez_value_architect import (
    ACTIVATION_STATE,
    EvidenceState,
    ValueCandidate,
    authority_gate,
    pareto_frontier,
    run,
    sha256,
)


def objective_vector(utility, capability, provenance):
    return {
        "utility": {"state": "MEASURED", "value": utility},
        "capability": {"state": "MEASURED", "value": capability},
        "optionality": {"state": "UNKNOWN"},
        "reusability": {"state": "UNKNOWN"},
        "provenance": {"state": "MEASURED", "value": provenance},
        "acquisition_readiness": {"state": "UNKNOWN"},
        "automation": {"state": "UNKNOWN"},
        "information_density": {"state": "MODELED", "value": 0.5},
    }


def candidate(candidate_id, vector):
    return ValueCandidate(
        candidate_id=candidate_id,
        generation=0,
        parent_ids=(),
        kind="test",
        title=candidate_id,
        description="test candidate",
        evidence_state=EvidenceState.PROPOSED.value,
        objective_vector=vector,
        unlock_targets=(),
        acquisition_routes=(),
        transformations=(),
        tests=(),
        falsifiers=("unknown_state_promoted_to_permission",),
        activation_state=ACTIVATION_STATE,
    )


class RecursiveValueArchitectTests(unittest.TestCase):
    def test_pareto_keeps_nondominated_candidates(self):
        a = candidate("a", objective_vector(0.9, 0.8, 0.9))
        b = candidate("b", objective_vector(0.7, 0.7, 0.7))
        c = candidate("c", objective_vector(0.9, 0.95, 0.6))
        frontier = {item.candidate_id for item in pareto_frontier([a, b, c])}
        self.assertEqual(frontier, {"a", "c"})

    def test_authority_gate_blocks_unknown_or_unauthorized_state(self):
        blocked = candidate("blocked", objective_vector(1, 1, 1))
        context = {
            "authorization": {"state": "UNKNOWN"},
            "tests": {"passed": True},
            "rollback": {"available": True},
            "evidence": {"chain_status": "VERIFIED"},
        }
        decision = authority_gate(context, blocked)
        self.assertFalse(decision["allowed_to_execute"])
        self.assertIn("authorization.state != AUTHORIZED", decision["failures"])

    def test_runtime_is_deterministic_for_same_input(self):
        context = {
            "assets": [
                {
                    "asset_id": "asset-demo",
                    "name": "Demo Asset",
                    "kind": "artifact",
                    "evidence_state": "OBSERVED",
                    "provenance": ["local:test"],
                    "capabilities": ["pipeline.run"],
                }
            ],
            "acquisition_routes": [
                {
                    "route_id": "route-public",
                    "asset_id": "asset-demo",
                    "method": "public",
                    "state": "PUBLIC",
                    "authorization_required": False,
                    "source": "local:test",
                }
            ],
            "transformations": [
                {
                    "transformation_id": "transform-demo",
                    "source_asset_ids": ["asset-demo"],
                    "output_kind": "test-harness",
                    "output_name": "Demo Test Harness",
                    "operation": "construct deterministic test harness",
                    "state": "PROPOSED",
                }
            ],
            "device": {"present": True},
            "storage": {"writable": True},
            "network": {"available": False},
            "sync": {"endpoint_configured": False},
            "runtime": {"healthy": True},
            "evidence": {"chain_status": "UNKNOWN"},
            "authorization": {"state": "UNKNOWN"},
            "rollback": {"available": True},
            "tests": {"passed": False},
            "artifact": {"provenance_complete": False},
            "voice": {"model_available": False},
            "music": {"engine_available": False},
            "policy": {"explicit_allow": False},
            "execution": {"mode": "NORMAL"},
        }
        first = run(context, generations=2, toroidal_generations=1, poles=4)
        second = run(context, generations=2, toroidal_generations=1, poles=4)
        self.assertEqual(
            first["recursive_value_architecture_sha256"],
            second["recursive_value_architecture_sha256"],
        )
        self.assertEqual(first["value_graph"]["assets"][0]["asset_id"], "asset-demo")

    def test_sha256_is_canonical(self):
        self.assertEqual(
            sha256({"b": 2, "a": 1}),
            sha256({"a": 1, "b": 2}),
        )


if __name__ == "__main__":
    unittest.main()
