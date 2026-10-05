#!/usr/bin/env python3
"""Metapolycentrifugal toroidal generative runtime for EVEZ-OS.

A torus of competing architecture centers. Each center:
  discover -> generate -> challenge -> exchange -> rotate -> reconcile.

"Miraculating" is the runtime's name for a bounded synthesis event: multiple
independent proposals produce a new candidate not identical to any parent.
It is a deterministic construction, not a claim of supernatural causation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    from evez_architect import discover, invent, evaluate, sha256
except ImportError:
    from mobile.evez_architect import discover, invent, evaluate, sha256


VERSION = "evez-metapolycentrifugal-torus/v1"


@dataclass(frozen=True)
class Pole:
    pole_id: str
    phase: float
    radius: float
    objective: str
    pressure: float


@dataclass(frozen=True)
class TorusCandidate:
    candidate_id: str
    torus_generation: int
    parent_ids: tuple[str, ...]
    synthesis_mode: str
    pole_ids: tuple[str, ...]
    mutation: str
    score: float
    viable: bool
    novelty: float
    stability: float
    circulation: float
    contradiction_retention: float
    architecture_sha256: str


OBJECTIVES = (
    "witness",
    "runtime",
    "capability",
    "synthesis",
    "review",
    "recovery",
    "compression",
    "exploration",
)


def _phase(seed: str, index: int) -> float:
    value = int(hashlib.sha256(f"{seed}:{index}".encode()).hexdigest()[:12], 16)
    return (value % 1_000_000) / 1_000_000 * 2 * math.pi


def poles(seed: str, count: int = 8) -> tuple[Pole, ...]:
    count = max(3, min(32, int(count)))
    return tuple(
        Pole(
            pole_id=f"p{index:02d}",
            phase=_phase(seed, index),
            radius=1.0 + 0.125 * (index % 4),
            objective=OBJECTIVES[index % len(OBJECTIVES)],
            pressure=round(0.35 + 0.10 * ((index * 7) % 5), 4),
        )
        for index in range(count)
    )


def toroidal_edges(poleset: tuple[Pole, ...]) -> tuple[tuple[str, str, str], ...]:
    n = len(poleset)
    edges = []
    for i, pole in enumerate(poleset):
        next_pole = poleset[(i + 1) % n]
        opposite = poleset[(i + n // 2) % n]
        edges.append((pole.pole_id, next_pole.pole_id, "circulation"))
        if opposite.pole_id != pole.pole_id:
            edges.append((pole.pole_id, opposite.pole_id, "centrifugal-crosslink"))
    return tuple(edges)


def field_state(
    context: dict[str, Any],
    poleset: tuple[Pole, ...],
    generation: int,
) -> dict[str, Any]:
    discovery = discover(context)
    unlocked = discovery["runtime"]["unlocked"]
    locked = discovery["runtime"]["locked"]
    unknown = discovery["runtime"]["unknown"]

    circulation = round(
        sum(abs(math.sin(p.phase + generation * 0.618)) * p.pressure for p in poleset)
        / max(1, len(poleset)),
        6,
    )
    centrifugal = round(
        sum(p.radius * p.pressure for p in poleset) / max(1, len(poleset)),
        6,
    )
    epistemic_friction = round(
        (len(unknown) + 2 * len(locked)) / max(1, len(unlocked) + len(locked) + len(unknown)),
        6,
    )

    return {
        "version": VERSION,
        "generation": generation,
        "discovery_sha256": discovery["discovery_sha256"],
        "unlocked_count": len(unlocked),
        "locked_count": len(locked),
        "unknown_count": len(unknown),
        "circulation": circulation,
        "centrifugal": centrifugal,
        "epistemic_friction": epistemic_friction,
    }


def miraculate(
    candidates: list[tuple[Any, Any]],
    poleset: tuple[Pole, ...],
    *,
    generation: int,
    context: dict[str, Any],
) -> TorusCandidate | None:
    viable = [(candidate, evaluation) for candidate, evaluation in candidates if evaluation.viable]
    if len(viable) < 2:
        return None

    # Select parents deterministically but from different toroidal regions.
    viable.sort(key=lambda pair: (-pair[1].score, pair[0].candidate_id))
    parents = viable[: min(4, len(viable))]
    parent_ids = tuple(parent.candidate_id for parent, _ in parents)

    mutation_material = {
        "generation": generation,
        "parents": parent_ids,
        "poles": [p.pole_id for p in poleset],
    }
    mutation = hashlib.sha256(json.dumps(mutation_material, sort_keys=True).encode()).hexdigest()[:12]

    field = field_state(context, poleset, generation)
    novelty = round(min(1.0, 0.35 + 0.15 * len(parent_ids)), 4)
    stability = round(max(0.0, 1.0 - field["epistemic_friction"]), 4)
    circulation = field["circulation"]
    contradiction_retention = round(
        1.0 if "contradiction" in [p.objective for p in poleset] else 0.75,
        4,
    )
    score = round(
        0.30 * novelty
        + 0.30 * stability
        + 0.20 * circulation
        + 0.20 * contradiction_retention,
        6,
    )

    payload = {
        "generation": generation,
        "parents": parent_ids,
        "mutation": mutation,
        "poles": [asdict(p) for p in poleset],
        "field": field,
        "score": score,
    }

    return TorusCandidate(
        candidate_id=sha256(payload)[:16],
        torus_generation=generation,
        parent_ids=parent_ids,
        synthesis_mode="MIRACULATION",
        pole_ids=tuple(p.pole_id for p in poleset),
        mutation=mutation,
        score=score,
        viable=True,
        novelty=novelty,
        stability=stability,
        circulation=circulation,
        contradiction_retention=contradiction_retention,
        architecture_sha256=sha256(payload),
    )


def run(
    context: dict[str, Any],
    *,
    generations: int = 4,
    pole_count: int = 8,
) -> dict[str, Any]:
    seed = sha256(context)
    poleset = poles(seed, pole_count)
    field_history = []
    candidates_history = []
    parents: list[tuple[Any, Any]] = []

    for generation in range(max(1, generations)):
        field = field_state(context, poleset, generation)
        field_history.append(field)

        invented = invent(discover(context), generation=generation)
        evaluated = [(candidate, evaluate(candidate, context)) for candidate in invented]
        evaluated.sort(key=lambda pair: (-pair[1].score, pair[0].candidate_id))
        selected = evaluated[: max(4, min(8, pole_count))]
        candidates_history.append([
            {"candidate_id": c.candidate_id, "evaluation": asdict(e)}
            for c, e in selected
        ])

        synthesized = miraculate(selected, poleset, generation=generation, context=context)
        if synthesized is not None:
            parents = [(synthesized, type("E", (), {"score": synthesized.score, "viable": synthesized.viable})())]
            candidates_history[-1].append({"miraculation": asdict(synthesized)})

    final = {
        "version": VERSION,
        "principle": "Many centers generate; none becomes sovereign; circulation changes the next generation.",
        "poles": [asdict(p) for p in poleset],
        "toroidal_edges": [list(edge) for edge in toroidal_edges(poleset)],
        "field_history": field_history,
        "candidate_history": candidates_history,
        "generation_count": len(field_history),
        "activation_state": "PROPOSAL_ONLY",
        "invariants": [
            "polycentric != single authority",
            "circulation != truth",
            "novelty != validity",
            "agreement != proof",
            "miraculation != supernatural claim",
            "proposal != activation",
            "UNKNOWN != permission",
        ],
    }
    final["toroidal_architecture_sha256"] = sha256(final)
    return final


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the EVEZ metapolycentrifugal toroidal generator.")
    parser.add_argument("context")
    parser.add_argument("--generations", type=int, default=4)
    parser.add_argument("--poles", type=int, default=8)
    parser.add_argument("--output")
    args = parser.parse_args()

    context = json.loads(Path(args.context).read_text(encoding="utf-8"))
    result = run(context, generations=args.generations, pole_count=args.poles)
    rendered = json.dumps(result, indent=2, sort_keys=True)

    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
