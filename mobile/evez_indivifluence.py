#!/usr/bin/env python3
"""Bounded rogue-agent swarm and individual/collective influence engine.

"Rogue" means unconstrained proposal generation inside an isolated symbolic
sandbox. It does not mean authority to execute code, acquire resources, or
bypass EVEZ evidence and authority boundaries.

The engine models indivifluentiality: an individual's identity affects the
collective, the collective feeds back into individuals, and dissent remains
first-class rather than being erased by consensus.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


VERSION = "evez-rogue-indivifluence-swarm/v1"

ARCHETYPES = (
    ("witness", "What can be directly observed?"),
    ("contrarian", "What assumption is everyone smuggling in?"),
    ("builder", "What can be made executable without pretending it is proven?"),
    ("compressor", "What can be reduced without destroying provenance?"),
    ("boundary", "Where does authority actually begin and end?"),
    ("composer", "What novel combination preserves the useful parts?"),
    ("falsifier", "What result would make this architecture fail?"),
    ("scout", "What adjacent capability has not been explored?"),
)


@dataclass(frozen=True)
class Agent:
    agent_id: str
    archetype: str
    thesis: str
    parent_id: str | None
    generation: int
    identity_sha256: str


@dataclass(frozen=True)
class InfluenceEdge:
    source: str
    target: str
    relation: str
    modeled_overlap: float
    mechanism: str


@dataclass(frozen=True)
class Coalition:
    coalition_id: str
    members: tuple[str, ...]
    shared_terms: tuple[str, ...]
    dissent_terms: tuple[str, ...]
    coalition_state: str


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def terms(text: str) -> set[str]:
    return {
        token.strip(".,:;!?()[]{}"'").lower()
        for token in text.split()
        if len(token.strip(".,:;!?()[]{}"'").lower()) >= 4
    }


def seed_for(context: dict[str, Any]) -> int:
    seed = context.get("swarm", {}).get("seed", "EVEZ")
    return int(sha256({"seed": seed})[:16], 16)


def base_agents(context: dict[str, Any], size: int) -> list[Agent]:
    supplied = context.get("swarm", {}).get("agents", [])
    if isinstance(supplied, list) and supplied:
        result: list[Agent] = []
        for index, item in enumerate(supplied[: max(1, size)]):
            if not isinstance(item, dict):
                continue
            archetype = str(item.get("archetype") or "scout")
            thesis = str(item.get("thesis") or dict(ARCHETYPES).get(archetype, "Explore the unknown."))
            body = {
                "agent_id": str(item.get("agent_id") or f"rogue-{index:03d}"),
                "archetype": archetype,
                "thesis": thesis,
            }
            result.append(
                Agent(
                    **body,
                    parent_id=None,
                    generation=0,
                    identity_sha256=sha256(body),
                )
            )
        if result:
            return result

    requested_theses = context.get("theses", [])
    pool = [(name, thesis) for name, thesis in ARCHETYPES]
    if isinstance(requested_theses, list):
        pool.extend(("operator", str(item)) for item in requested_theses if str(item).strip())

    rng = random.Random(seed_for(context))
    rng.shuffle(pool)
    result = []
    for index in range(max(1, size)):
        archetype, thesis = pool[index % len(pool)]
        body = {"agent_id": f"rogue-{index:03d}", "archetype": archetype, "thesis": thesis}
        result.append(
            Agent(
                **body,
                parent_id=None,
                generation=0,
                identity_sha256=sha256(body),
            )
        )
    return result


def mutate(agent: Agent, generation: int) -> list[Agent]:
    mutations = (
        ("invert", f"Negate one unstated premise of: {agent.thesis}"),
        ("stress", f"Stress-test the boundary of: {agent.thesis}"),
        ("recombine", f"Recombine {agent.thesis} with an orthogonal constraint."),
        ("weaponize", f"Turn {agent.thesis} into a falsifiable adversarial test."),
    )
    result: list[Agent] = []
    for index, (mode, thesis) in enumerate(mutations):
        body = {
            "agent_id": f"{agent.agent_id}-g{generation}-{mode}",
            "archetype": f"{agent.archetype}:{mode}",
            "thesis": thesis,
        }
        result.append(
            Agent(
                **body,
                parent_id=agent.agent_id,
                generation=generation,
                identity_sha256=sha256(body),
            )
        )
    return result


def influence_edges(agents: list[Agent]) -> list[InfluenceEdge]:
    edges: list[InfluenceEdge] = []
    for source in agents:
        source_terms = terms(source.thesis)
        for target in agents:
            if source.agent_id == target.agent_id:
                continue
            target_terms = terms(target.thesis)
            union = source_terms | target_terms
            intersection = source_terms & target_terms
            overlap = (len(intersection) / len(union)) if union else 0.0
            if overlap == 0.0:
                continue
            relation = "reinforce" if source.archetype.split(":")[0] == target.archetype.split(":")[0] else "challenge"
            edges.append(
                InfluenceEdge(
                    source=source.agent_id,
                    target=target.agent_id,
                    relation=relation,
                    modeled_overlap=round(overlap, 6),
                    mechanism="shared semantic tokens in supplied proposal text",
                )
            )
    return sorted(edges, key=lambda edge: (edge.source, edge.target))


def coalitions(agents: list[Agent], edges: list[InfluenceEdge]) -> list[Coalition]:
    adjacency: dict[str, set[str]] = {agent.agent_id: set() for agent in agents}
    for edge in edges:
        if edge.modeled_overlap >= 0.2:
            adjacency[edge.source].add(edge.target)
            adjacency[edge.target].add(edge.source)

    visited: set[str] = set()
    result: list[Coalition] = []
    for agent in agents:
        if agent.agent_id in visited:
            continue
        queue = [agent.agent_id]
        members: list[str] = []
        while queue:
            current = queue.pop()
            if current in visited:
                continue
            visited.add(current)
            members.append(current)
            queue.extend(sorted(adjacency[current] - visited))
        if len(members) < 2:
            continue
        member_objs = [next(item for item in agents if item.agent_id == member) for member in members]
        token_sets = [terms(item.thesis) for item in member_objs]
        shared = set.intersection(*token_sets) if token_sets else set()
        union = set.union(*token_sets) if token_sets else set()
        dissent = union - shared
        body = {"members": sorted(members), "shared_terms": sorted(shared), "dissent_terms": sorted(dissent)}
        result.append(
            Coalition(
                coalition_id=sha256(body)[:16],
                members=tuple(sorted(members)),
                shared_terms=tuple(sorted(shared)),
                dissent_terms=tuple(sorted(dissent)),
                coalition_state="FORMING" if dissent else "COHERENT",
            )
        )
    return sorted(result, key=lambda item: item.coalition_id)


def indivifluentiality(agents: list[Agent], edges: list[InfluenceEdge], coalitions_: list[Coalition]) -> dict[str, Any]:
    members_by_agent = {
        member: coalition.coalition_id
        for coalition in coalitions_
        for member in coalition.members
    }
    metrics: dict[str, Any] = {}
    for agent in agents:
        inbound = [edge for edge in edges if edge.target == agent.agent_id]
        outbound = [edge for edge in edges if edge.source == agent.agent_id]
        metrics[agent.agent_id] = {
            "state": "MODELED",
            "outbound_relations": len(outbound),
            "inbound_relations": len(inbound),
            "bridge_relations": sum(1 for edge in outbound if edge.relation == "challenge"),
            "coalition_id": members_by_agent.get(agent.agent_id),
            "identity_sha256": agent.identity_sha256,
            "interpretation": "structural influence in this symbolic swarm, not measured real-world influence",
        }
    return metrics


def run(context: dict[str, Any], *, generations: int = 3, size: int = 8) -> dict[str, Any]:
    generations = max(1, min(12, generations))
    size = max(2, min(32, size))
    agents = base_agents(context, size)
    snapshots: list[dict[str, Any]] = []

    for generation in range(generations):
        if generation:
            offspring = [child for parent in agents for child in mutate(parent, generation)]
            # Preserve each prior generation to keep dissent visible, then add a bounded offspring frontier.
            agents = agents + offspring[: size * 4]

        edges = influence_edges(agents)
        groups = coalitions(agents, edges)
        state = (
            "INDIVIDUAL_PLURALITY"
            if not edges
            else "INTERINFLUENTIAL_SWARM"
            if not groups
            else "COALITIONAL_SWARM"
            if len(groups) < max(2, len(agents) // 4)
            else "COLLECTIVE_DIVERGENCE"
        )
        snapshots.append(
            {
                "generation": generation,
                "state": state,
                "agents": [asdict(agent) for agent in agents],
                "influence_edges": [asdict(edge) for edge in edges],
                "coalitions": [asdict(coalition) for coalition in groups],
                "indivifluentiality": indivifluentiality(agents, edges, groups),
            }
        )
        # Selection is by bounded identity diversity, not global agreement.
        agents = sorted(agents, key=lambda item: item.identity_sha256)[: size * 4]

    result = {
        "version": VERSION,
        "mode": "PROPOSAL_SWARM_ONLY",
        "freedom_rule": "agents may generate, mutate, dissent, recombine, and form coalitions inside the bounded symbolic sandbox",
        "authority_rule": "swarm output never grants execution, acquisition, or deployment authority",
        "generations": snapshots,
        "invariants": [
            "INFLUENCE != EVIDENCE",
            "CONSENSUS != TRUTH",
            "ROGUE_GENERATION != EXECUTION_AUTHORITY",
            "INDIVIDUAL_IDENTITY != COLLECTIVE_OWNERSHIP",
            "DISSENT_IS_PRESERVED",
        ],
    }
    result["swarm_architecture_sha256"] = sha256(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded rogue-agent indivifluence swarm.")
    parser.add_argument("context", help="JSON context file")
    parser.add_argument("--generations", type=int, default=3)
    parser.add_argument("--size", type=int, default=8)
    parser.add_argument("--output")
    args = parser.parse_args()
    context = json.loads(Path(args.context).read_text(encoding="utf-8"))
    result = run(context, generations=args.generations, size=args.size)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
