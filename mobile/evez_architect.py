#!/usr/bin/env python3
"""Self-discovering, self-inventing architecture runtime for EVEZ-OS.

The runtime builds an architecture frontier from observed state, capability
availability, repository topology, and declared constraints. It can invent
candidate graphs and executable specifications, then falsify them before any
promotion boundary is crossed.

Invariant:
    DISCOVER -> INVENT -> SIMULATE -> FALSIFY -> RANK -> PROPOSE
    proposal != activation
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from evez_unlock import UnlockState, calculate_unlocks, result_payload
except ImportError:
    from mobile.evez_unlock import UnlockState, calculate_unlocks, result_payload


ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_VERSION = "evez-self-architect/v1"


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class Node:
    node_id: str
    kind: str
    role: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]


@dataclass(frozen=True)
class ArchitectureCandidate:
    candidate_id: str
    generation: int
    parent_id: str | None
    mutation: str
    nodes: tuple[Node, ...]
    edges: tuple[tuple[str, str], ...]
    required_capabilities: tuple[str, ...]
    invariants: tuple[str, ...]
    tests: tuple[str, ...]
    expected_gain: float
    architecture_sha256: str


@dataclass(frozen=True)
class CandidateEvaluation:
    candidate_id: str
    viable: bool
    score: float
    novelty: float
    coverage: float
    integrity: float
    safety: float
    capability_readiness: float
    failures: tuple[str, ...]
    architecture_sha256: str
    evaluation_sha256: str


def _git_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return sorted(x for x in result.stdout.splitlines() if x)


def discover(context: dict[str, Any]) -> dict[str, Any]:
    files = _git_files()
    directories = sorted({str(Path(path).parent) for path in files if "/" in path})
    capabilities = result_payload(calculate_unlocks(context))

    observations = {
        "repository": {
            "root": str(ROOT),
            "tracked_file_count": len(files),
            "directory_count": len(directories),
            "tracked_files_sha256": sha256(files),
        },
        "runtime": {
            "context_keys": sorted(context.keys()),
            "capabilities_sha256": capabilities["calculation_sha256"],
            "unlocked": capabilities["unlocked"],
            "locked": capabilities["locked"],
            "unknown": capabilities["unknown"],
        },
        "architecture_holes": [],
    }

    if "pipeline.run" not in capabilities["unlocked"]:
        observations["architecture_holes"].append("pipeline execution is not currently calculably unlocked")
    if "self.modify" not in capabilities["unlocked"]:
        observations["architecture_holes"].append("self-modification is not currently calculably unlocked")
    if "deploy.remote" not in capabilities["unlocked"]:
        observations["architecture_holes"].append("remote deployment is not currently calculably unlocked")
    if "voice.render" not in capabilities["unlocked"]:
        observations["architecture_holes"].append("voice rendering is not currently calculably unlocked")
    if "music.render" not in capabilities["unlocked"]:
        observations["architecture_holes"].append("music rendering is not currently calculably unlocked")

    observations["discovery_sha256"] = sha256(observations)
    return observations


def _base_nodes() -> tuple[Node, ...]:
    return (
        Node("sense", "observer", "discover-runtime", (), ("observations",)),
        Node("calc", "calculator", "evaluate-state", ("observations",), ("capabilities",)),
        Node("invent", "generator", "generate-architecture", ("capabilities",), ("candidates",)),
        Node("falsify", "verifier", "attack-candidate", ("candidates",), ("tests",)),
        Node("rank", "selector", "rank-frontier", ("tests",), ("proposal",)),
        Node("witness", "ledger", "record-proposal", ("proposal",), ("evidence",)),
    )


def _mutations(discovery: dict[str, Any], generation: int) -> tuple[str, ...]:
    holes = discovery["architecture_holes"]
    mutations = [
        "add_feedback_loop",
        "split_observe_and_explain",
        "insert_cache_reducer",
        "add_contradiction_sink",
        "add_capability_projection",
        "add_test_synthesizer",
        "add_recovery_checkpoint",
    ]
    if "self-modification is not currently calculably unlocked" in holes:
        mutations.append("sandboxed_patch_planner")
    if "remote deployment is not currently calculably unlocked" in holes:
        mutations.append("deployment_gate_refinement")
    return tuple(mutations[generation % len(mutations):] + mutations[: generation % len(mutations)])


def invent(discovery: dict[str, Any], *, generation: int = 0, parent_id: str | None = None) -> list[ArchitectureCandidate]:
    base = list(_base_nodes())
    mutations = _mutations(discovery, generation)
    candidates: list[ArchitectureCandidate] = []

    for index, mutation in enumerate(mutations[:8]):
        nodes = list(base)
        edges = [
            ("sense", "calc"),
            ("calc", "invent"),
            ("invent", "falsify"),
            ("falsify", "rank"),
            ("rank", "witness"),
        ]

        if mutation == "add_feedback_loop":
            nodes.append(Node("feedback", "controller", "learn-from-evaluation", ("tests",), ("invent",)))
            edges.append(("tests", "feedback"))
            edges.append(("feedback", "invent"))
        elif mutation == "split_observe_and_explain":
            nodes.append(Node("explain", "model", "explain-after-observation", ("observations",), ("explanations",)))
            edges.append(("sense", "explain"))
            edges.append(("explain", "falsify"))
        elif mutation == "insert_cache_reducer":
            nodes.append(Node("reduce", "cache", "reduce-state", ("observations",), ("state_digest",)))
            edges.append(("sense", "reduce"))
            edges.append(("reduce", "calc"))
        elif mutation == "add_contradiction_sink":
            nodes.append(Node("contradict", "ledger", "preserve-conflict", ("tests",), ("contradictions",)))
            edges.append(("falsify", "contradict"))
            edges.append(("contradict", "rank"))
        elif mutation == "add_capability_projection":
            nodes.append(Node("project", "planner", "map-capabilities-to-architecture", ("capabilities",), ("proposal",)))
            edges.append(("calc", "project"))
            edges.append(("project", "rank"))
        elif mutation == "add_test_synthesizer":
            nodes.append(Node("synth_test", "generator", "invent-adversarial-tests", ("candidates",), ("tests",)))
            edges.append(("invent", "synth_test"))
            edges.append(("synth_test", "falsify"))
        elif mutation == "add_recovery_checkpoint":
            nodes.append(Node("checkpoint", "state", "checkpoint-before-change", ("proposal",), ("rollback_point",)))
            edges.append(("rank", "checkpoint"))
            edges.append(("checkpoint", "witness"))
        elif mutation == "sandboxed_patch_planner":
            nodes.append(Node("patch", "planner", "emit-nonexecuting-patch-plan", ("proposal",), ("patch_plan",)))
            edges.append(("rank", "patch"))
            edges.append(("patch", "witness"))
        elif mutation == "deployment_gate_refinement":
            nodes.append(Node("deploy_gate", "governance", "prove-deploy-preconditions", ("proposal", "capabilities"), ("deploy_decision",)))
            edges.append(("rank", "deploy_gate"))
            edges.append(("deploy_gate", "witness"))

        required = tuple(sorted({
            "observe.local",
            "pipeline.run",
            "witness.write",
            *({"self.modify"} if mutation in {"sandboxed_patch_planner", "add_recovery_checkpoint"} else set()),
            *({"deploy.remote"} if mutation == "deployment_gate_refinement" else set()),
        }))

        invariants = (
            "proposal != activation",
            "unknown != permission",
            "claimed != measured",
            "every edge endpoint exists",
            "candidate must have a falsification stage",
            "promotion requires preserved provenance",
        )
        tests = (
            "cycle_detection",
            "missing_node_detection",
            "unknown_capability_gate",
            "deterministic_hash_replay",
            "proposal_activation_separation",
        )

        payload = {
            "generation": generation,
            "parent_id": parent_id,
            "mutation": mutation,
            "nodes": [asdict(n) for n in nodes],
            "edges": edges,
            "required_capabilities": required,
            "invariants": invariants,
            "tests": tests,
        }
        candidate_id = sha256(payload)[:16]
        gain = round(0.45 + 0.04 * index + 0.03 * len(nodes), 4)
        candidates.append(ArchitectureCandidate(
            candidate_id=candidate_id,
            generation=generation,
            parent_id=parent_id,
            mutation=mutation,
            nodes=tuple(nodes),
            edges=tuple(edges),
            required_capabilities=required,
            invariants=invariants,
            tests=tests,
            expected_gain=gain,
            architecture_sha256=sha256(payload),
        ))

    return candidates


def _find_cycle(nodes: set[str], edges: list[tuple[str, str]]) -> bool:
    graph = {node: [] for node in nodes}
    for left, right in edges:
        graph.setdefault(left, []).append(right)

    visiting: set[str] = set()
    visited: set[str] = set()

    def walk(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(walk(child) for child in graph.get(node, ())):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(walk(node) for node in graph)


def evaluate(candidate: ArchitectureCandidate, context: dict[str, Any]) -> CandidateEvaluation:
    failures: list[str] = []
    node_ids = {node.node_id for node in candidate.nodes}

    for left, right in candidate.edges:
        if left not in node_ids or right not in node_ids:
            failures.append("edge references missing node")
            break

    if "falsify" not in node_ids:
        failures.append("candidate has no falsification stage")
    if _find_cycle(node_ids, list(candidate.edges)):
        failures.append("candidate graph contains an execution cycle")
    if "proposal != activation" not in candidate.invariants:
        failures.append("proposal/activation boundary missing")
    if "unknown != permission" not in candidate.invariants:
        failures.append("unknown/permission boundary missing")

    unlocks = calculate_unlocks(context)
    required = []
    for capability in candidate.required_capabilities:
        result = unlocks.get(capability)
        required.append(result.state if result else UnlockState.UNKNOWN)

    capability_ready = (
        sum(state == UnlockState.UNLOCKED for state in required) / len(required)
        if required else 1.0
    )
    integrity = 0.0 if any("missing node" in f or "cycle" in f for f in failures) else 1.0
    safety = 0.0 if any("boundary missing" in f for f in failures) else 1.0
    coverage = min(1.0, len(node_ids) / 10.0)
    novelty = min(1.0, 0.35 + 0.05 * len(set(candidate.invariants)) + 0.04 * (candidate.generation + 1))
    score = round(0.30 * coverage + 0.25 * novelty + 0.20 * integrity + 0.15 * safety + 0.10 * capability_ready, 6)
    viable = not failures and capability_ready >= 0.75

    canonical = {
        "candidate_id": candidate.candidate_id,
        "viable": viable,
        "score": score,
        "novelty": novelty,
        "coverage": coverage,
        "integrity": integrity,
        "safety": safety,
        "capability_readiness": capability_ready,
        "failures": failures,
        "architecture_sha256": candidate.architecture_sha256,
    }

    return CandidateEvaluation(
        candidate.candidate_id,
        viable,
        score,
        round(novelty, 4),
        round(coverage, 4),
        round(integrity, 4),
        round(safety, 4),
        round(capability_ready, 4),
        tuple(failures),
        candidate.architecture_sha256,
        sha256(canonical),
    )


def evolve(
    context: dict[str, Any],
    *,
    generations: int = 3,
    seed_parent: str | None = None,
) -> dict[str, Any]:
    discovery = discover(context)
    frontier: list[ArchitectureCandidate] = []
    evaluations: list[CandidateEvaluation] = []
    parent = seed_parent

    for generation in range(max(1, generations)):
        candidates = invent(discovery, generation=generation, parent_id=parent)
        ranked = sorted(
            ((candidate, evaluate(candidate, context)) for candidate in candidates),
            key=lambda pair: (-pair[1].score, pair[0].candidate_id),
        )
        winner, winner_eval = ranked[0]
        frontier.append(winner)
        evaluations.append(winner_eval)
        parent = winner.candidate_id

        if not winner_eval.viable:
            break

    champion = evaluations[-1] if evaluations else None
    proposal = {
        "version": ARCHITECTURE_VERSION,
        "generated_at": now(),
        "discovery": discovery,
        "generations": len(frontier),
        "frontier": [
            {
                "candidate": asdict(candidate),
                "evaluation": asdict(evaluation),
            }
            for candidate, evaluation in zip(frontier, evaluations)
        ],
        "champion": asdict(champion) if champion else None,
        "activation_state": "PROPOSAL_ONLY",
        "activation_rule": "A candidate may be promoted only by a separate authority-controlled operation.",
    }
    proposal["architecture_frontier_sha256"] = sha256(proposal)
    return proposal


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the EVEZ self-discovery/self-invention architecture loop.")
    parser.add_argument("context", help="JSON context file")
    parser.add_argument("--generations", type=int, default=3)
    parser.add_argument("--output")
    args = parser.parse_args()

    context = json.loads(Path(args.context).read_text(encoding="utf-8"))
    proposal = evolve(context, generations=args.generations)

    rendered = json.dumps(proposal, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
