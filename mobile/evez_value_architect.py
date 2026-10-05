#!/usr/bin/env python3
"""Recursive value-architecture runtime for EVEZ-OS.

This runtime turns the luxury recursive-value prompt into a bounded,
evidence-aware planning engine.

Core loop:
  OBSERVE -> EXTRACT -> NORMALIZE -> DECOMPOSE -> MODEL -> CALCULATE
  -> REVERSE_ENGINEER -> GENERATE -> TEST -> FALSIFY -> FRONTIER
  -> ACQUISITION_PLAN -> TRANSFORM -> PACKAGE -> WITNESS -> RECIRCULATE

The runtime never treats a proposal, estimate, or authorization claim as
execution authority. Generated assets are proposals until independently
validated and authorized.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

try:
    from evez_architect import discover, polycentric_frontier
    from evez_toroid import run as toroidal_run
    from evez_unlock import calculate_unlocks, result_payload
except ImportError:
    from mobile.evez_architect import discover, polycentric_frontier
    from mobile.evez_toroid import run as toroidal_run
    from mobile.evez_unlock import calculate_unlocks, result_payload


VERSION = "evez-recursive-value-architect/v1"
ACTIVATION_STATE = "PROPOSAL_ONLY"

OBJECTIVES = (
    "utility",
    "capability",
    "optionality",
    "reusability",
    "provenance",
    "acquisition_readiness",
    "automation",
    "information_density",
)


class EvidenceState(StrEnum):
    OBSERVED = "OBSERVED"
    INFERRED = "INFERRED"
    PROPOSED = "PROPOSED"
    MODELED = "MODELED"
    MEASURED = "MEASURED"
    VERIFIED = "VERIFIED"
    UNKNOWN = "UNKNOWN"
    STALE = "STALE"
    CONTRADICTED = "CONTRADICTED"
    RETRACTED = "RETRACTED"


class AcquisitionState(StrEnum):
    UNKNOWN = "UNKNOWN"
    PUBLIC = "PUBLIC"
    LICENSED = "LICENSED"
    AUTHORIZED = "AUTHORIZED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class Asset:
    asset_id: str
    name: str
    kind: str
    evidence_state: str
    provenance: tuple[str, ...]
    capabilities: tuple[str, ...]
    dependencies: tuple[str, ...]
    acquisition_route_ids: tuple[str, ...]


@dataclass(frozen=True)
class AcquisitionRoute:
    route_id: str
    asset_id: str
    method: str
    state: str
    authorization_required: bool
    authorization_state: str
    source: str
    constraints: tuple[str, ...]


@dataclass(frozen=True)
class Transformation:
    transformation_id: str
    source_asset_ids: tuple[str, ...]
    output_kind: str
    output_name: str
    operation: str
    state: str
    prerequisites: tuple[str, ...]


@dataclass(frozen=True)
class ValueCandidate:
    candidate_id: str
    generation: int
    parent_ids: tuple[str, ...]
    focus: str
    kind: str
    title: str
    description: str
    evidence_state: str
    objective_vector: dict[str, Any]
    unlock_targets: tuple[str, ...]
    acquisition_routes: tuple[str, ...]
    transformations: tuple[str, ...]
    tests: tuple[str, ...]
    falsifiers: tuple[str, ...]
    activation_state: str


@dataclass(frozen=True)
class LootArtifact:
    artifact_id: str
    candidate_id: str
    name: str
    artifact_kind: str
    value_claim: str
    evidence_state: str
    provenance: tuple[str, ...]
    next_action: str


@dataclass(frozen=True)
class LedgerEvent:
    sequence: int
    event_type: str
    payload: dict[str, Any]
    parent_hash: str | None
    event_hash: str


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _state(raw: Any, default: EvidenceState.UNKNOWN) -> str:
    value = str(raw or default.value).upper()
    return value if value in {state.value for state in EvidenceState} else default.value


def _route_state(raw: Any) -> str:
    value = str(raw or AcquisitionState.UNKNOWN.value).upper()
    return value if value in {state.value for state in AcquisitionState} else AcquisitionState.UNKNOWN.value


def _tuple_strings(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item) for item in value)


def normalize(context: dict[str, Any]) -> dict[str, Any]:
    """Normalize user-supplied inputs without inventing missing assets."""
    raw_assets = context.get("assets", [])
    raw_routes = context.get("acquisition_routes", [])
    raw_transforms = context.get("transformations", [])

    assets: list[Asset] = []
    for index, item in enumerate(raw_assets if isinstance(raw_assets, list) else []):
        if not isinstance(item, dict):
            continue
        asset_id = str(item.get("asset_id") or f"asset-{index:03d}")
        assets.append(
            Asset(
                asset_id=asset_id,
                name=str(item.get("name") or asset_id),
                kind=str(item.get("kind") or "UNKNOWN"),
                evidence_state=_state(item.get("evidence_state")),
                provenance=_tuple_strings(item.get("provenance")),
                capabilities=_tuple_strings(item.get("capabilities")),
                dependencies=_tuple_strings(item.get("dependencies")),
                acquisition_route_ids=_tuple_strings(item.get("acquisition_route_ids")),
            )
        )

    routes: list[AcquisitionRoute] = []
    for index, item in enumerate(raw_routes if isinstance(raw_routes, list) else []):
        if not isinstance(item, dict):
            continue
        route_id = str(item.get("route_id") or f"route-{index:03d}")
        routes.append(
            AcquisitionRoute(
                route_id=route_id,
                asset_id=str(item.get("asset_id") or ""),
                method=str(item.get("method") or "UNKNOWN"),
                state=_route_state(item.get("state")),
                authorization_required=bool(item.get("authorization_required", True)),
                authorization_state=str(item.get("authorization_state") or "UNKNOWN").upper(),
                source=str(item.get("source") or "UNKNOWN"),
                constraints=_tuple_strings(item.get("constraints")),
            )
        )

    transforms: list[Transformation] = []
    for index, item in enumerate(raw_transforms if isinstance(raw_transforms, list) else []):
        if not isinstance(item, dict):
            continue
        transform_id = str(item.get("transformation_id") or f"transform-{index:03d}")
        transforms.append(
            Transformation(
                transformation_id=transform_id,
                source_asset_ids=_tuple_strings(item.get("source_asset_ids")),
                output_kind=str(item.get("output_kind") or "artifact"),
                output_name=str(item.get("output_name") or transform_id),
                operation=str(item.get("operation") or "UNKNOWN"),
                state=_state(item.get("state"), EvidenceState.PROPOSED),
                prerequisites=_tuple_strings(item.get("prerequisites")),
            )
        )

    graph = {
        "assets": [asdict(item) for item in assets],
        "acquisition_routes": [asdict(item) for item in routes],
        "transformations": [asdict(item) for item in transforms],
        "constraints": context.get("constraints", {}),
        "objectives": context.get("objectives", {}),
    }
    graph["graph_sha256"] = sha256(graph)
    return graph


def reverse_engineer(asset: Asset, routes: list[AcquisitionRoute]) -> dict[str, Any]:
    related = [route for route in routes if route.asset_id == asset.asset_id]
    observable = {
        "asset_identity": asset.asset_id,
        "name": asset.name,
        "kind": asset.kind,
        "declared_evidence_state": asset.evidence_state,
        "provenance": list(asset.provenance),
        "dependencies": list(asset.dependencies),
        "capabilities": list(asset.capabilities),
        "authorized_routes": [
            route.route_id
            for route in related
            if route.state in {
                AcquisitionState.PUBLIC.value,
                AcquisitionState.LICENSED.value,
                AcquisitionState.AUTHORIZED.value,
            }
            and (
                not route.authorization_required
                or route.authorization_state == "AUTHORIZED"
            )
        ],
        "unknowns": [],
    }
    for route in related:
        if route.state == AcquisitionState.UNKNOWN.value:
            observable["unknowns"].append(f"route:{route.route_id}:state")
        if route.authorization_required and route.authorization_state != "AUTHORIZED":
            observable["unknowns"].append(f"route:{route.route_id}:authorization")
    if not asset.provenance:
        observable["unknowns"].append("asset:provenance")
    if asset.evidence_state == EvidenceState.UNKNOWN.value:
        observable["unknowns"].append("asset:evidence_state")
    observable["reverse_engineering_state"] = (
        EvidenceState.OBSERVED.value if not observable["unknowns"] else EvidenceState.INFERRED.value
    )
    observable["analysis_sha256"] = sha256(observable)
    return observable


def explicit_measurement(
    context: dict[str, Any],
    dimension: str,
    fallback: Any = None,
) -> dict[str, Any]:
    """Read an explicitly supplied objective measurement; never fabricate one."""
    objective_source = context.get("objective_measurements", {})
    if not isinstance(objective_source, dict):
        return {"state": EvidenceState.UNKNOWN.value, "value": fallback}
    value = objective_source.get(dimension)
    if isinstance(value, dict) and "value" in value:
        return {
            "state": _state(value.get("state"), EvidenceState.UNKNOWN),
            "value": value.get("value"),
            "source": value.get("source"),
        }
    if isinstance(value, (int, float)):
        return {
            "state": EvidenceState.MEASURED.value,
            "value": value,
            "source": "context.objective_measurements",
        }
    return {"state": EvidenceState.UNKNOWN.value, "value": fallback}


def model_information_density(graph: dict[str, Any]) -> dict[str, Any]:
    fields = (
        ("assets", graph.get("assets", [])),
        ("routes", graph.get("acquisition_routes", [])),
        ("transformations", graph.get("transformations", [])),
        ("constraints", graph.get("constraints", {})),
    )
    present = sum(1 for _, value in fields if value)
    return {
        "state": EvidenceState.MODELED.value,
        "field_groups_present": present,
        "field_groups_total": len(fields),
        "definition": "observed structural coverage of the supplied value graph",
    }


def candidate_objectives(context: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    vector: dict[str, Any] = {}
    for objective in OBJECTIVES:
        if objective == "information_density":
            vector[objective] = model_information_density(graph)
        else:
            vector[objective] = explicit_measurement(context, objective)
    return vector


def dominance(a: ValueCandidate, b: ValueCandidate) -> bool:
    comparable = []
    strictly_better = False
    for dimension in OBJECTIVES:
        left = a.objective_vector.get(dimension, {})
        right = b.objective_vector.get(dimension, {})
        if not isinstance(left, dict) or not isinstance(right, dict):
            continue
        lv, rv = left.get("value"), right.get("value")
        if not isinstance(lv, (int, float)) or not isinstance(rv, (int, float)):
            continue
        comparable.append(dimension)
        if lv < rv:
            return False
        if lv > rv:
            strictly_better = True
    return bool(comparable) and strictly_better


def pareto_frontier(candidates: list[ValueCandidate]) -> list[ValueCandidate]:
    frontier: list[ValueCandidate] = []
    for candidate in candidates:
        dominated = any(
            other.candidate_id != candidate.candidate_id and dominance(other, candidate)
            for other in candidates
        )
        if not dominated:
            frontier.append(candidate)
    return sorted(frontier, key=lambda item: item.candidate_id)


def legal_routes(
    routes: list[AcquisitionRoute],
    asset_ids: set[str],
) -> list[AcquisitionRoute]:
    allowed = {
        AcquisitionState.PUBLIC.value,
        AcquisitionState.LICENSED.value,
        AcquisitionState.AUTHORIZED.value,
    }
    return [
        route
        for route in routes
        if route.asset_id in asset_ids
        and route.state in allowed
        and (
            not route.authorization_required
            or route.authorization_state == "AUTHORIZED"
        )
    ]


def authority_gate(
    context: dict[str, Any],
    candidate: ValueCandidate,
) -> dict[str, Any]:
    authorization = str(
        context.get("authorization", {}).get("state", "UNKNOWN")
    ).upper()
    tests_passed = bool(context.get("tests", {}).get("passed", False))
    rollback = bool(context.get("rollback", {}).get("available", False))
    evidence_status = str(
        context.get("evidence", {}).get("chain_status", "UNKNOWN")
    ).upper()

    failures = []
    if authorization != "AUTHORIZED":
        failures.append("authorization.state != AUTHORIZED")
    if not tests_passed:
        failures.append("tests.passed != true")
    if not rollback:
        failures.append("rollback.available != true")
    if evidence_status != "VERIFIED":
        failures.append("evidence.chain_status != VERIFIED")
    if candidate.activation_state != ACTIVATION_STATE:
        failures.append("candidate activation boundary missing")

    return {
        "candidate_id": candidate.candidate_id,
        "allowed_to_execute": not failures,
        "decision": "AUTHORIZED" if not failures else "BLOCKED",
        "failures": failures,
        "rule": "proposal -> validation -> separate authority -> activation",
        "decision_sha256": sha256(
            {
                "candidate_id": candidate.candidate_id,
                "allowed_to_execute": not failures,
                "failures": failures,
            }
        ),
    }


FOCUS_ROTATION = (
    "measurement_reduction",
    "capability_unlock",
    "provenance_strengthening",
    "lawful_acquisition",
    "transformation_composition",
    "automation_reuse",
)


def make_candidate(
    context: dict[str, Any],
    graph: dict[str, Any],
    unlock_payload: dict[str, Any],
    *,
    generation: int,
    parent_ids: tuple[str, ...] = (),
) -> ValueCandidate:
    unlocked = set(unlock_payload["unlocked"])
    unknown = set(unlock_payload["unknown"])
    asset_ids = {item["asset_id"] for item in graph["assets"]}

    unlock_targets = tuple(sorted({
        capability for capability in (
            "pipeline.run",
            "self.modify",
            "deploy.remote",
            "voice.render",
            "music.render",
        )
        if capability in unknown or capability not in unlocked
    }))

    transformations = tuple(
        item["transformation_id"]
        for item in graph["transformations"]
    )
    routes = tuple(
        route["route_id"]
        for route in graph["acquisition_routes"]
        if route["asset_id"] in asset_ids
    )

    focus = FOCUS_ROTATION[generation % len(FOCUS_ROTATION)]
    title = (
        "Recursive Value Acquisition and Transformation Plan"
        if generation == 0
        else f"Generation {generation}: Recursive Frontier Recomposition [{focus}]"
    )
    description = (
        "Compose only evidence-backed or explicitly labeled proposed assets, "
        "preserve unknowns, identify legal acquisition routes, and produce "
        "reusable transformations without crossing the activation boundary."
    )

    tests = (
        "deterministic_hash_replay",
        "unknown_state_preservation",
        "pareto_non_dominance_check",
        "lawful_acquisition_filter",
        "authority_gate_check",
    )
    falsifiers = (
        "unverifiable_provenance",
        "unauthorized_acquisition_route",
        "unknown_state_promoted_to_permission",
        "failed_required_test",
        "activation_without_separate_authority",
    )

    payload = {
        "generation": generation,
        "parent_ids": parent_ids,
        "focus": focus,
        "title": title,
        "unlock_targets": unlock_targets,
        "routes": routes,
        "transformations": transformations,
    }
    candidate_id = sha256(payload)[:16]
    vector = candidate_objectives(context, graph)
    return ValueCandidate(
        candidate_id=candidate_id,
        generation=generation,
        parent_ids=parent_ids,
        focus=focus,
        kind="value_architecture",
        title=title,
        description=description,
        evidence_state=EvidenceState.PROPOSED.value,
        objective_vector=vector,
        unlock_targets=unlock_targets,
        acquisition_routes=routes,
        transformations=transformations,
        tests=tests,
        falsifiers=falsifiers,
        activation_state=ACTIVATION_STATE,
    )


def loot_from_candidate(
    candidate: ValueCandidate,
    graph: dict[str, Any],
) -> list[LootArtifact]:
    artifacts = [
        ("value-graph", "normalized_value_graph", "A canonical asset, route, and transformation graph."),
        ("research-compression", "research_compression_packet", "A compact provenance-preserving research packet."),
        ("unlock-map", "capability_unlock_map", "A calculable capability state map without authorization leakage."),
        ("reverse-engineering", "reverse_engineering_plan", "A lawful observable/decomposition plan."),
        ("acquisition", "lawful_acquisition_plan", "A filtered inventory of public, licensed, or authorized routes."),
        ("test-suite", "adversarial_test_suite", "A bounded test and falsifier set for the proposed value architecture."),
    ]
    result = []
    for name, kind, claim in artifacts:
        artifact_id = sha256({"candidate": candidate.candidate_id, "name": name})[:16]
        result.append(
            LootArtifact(
                artifact_id=artifact_id,
                candidate_id=candidate.candidate_id,
                name=name,
                artifact_kind=kind,
                value_claim=claim,
                evidence_state=EvidenceState.PROPOSED.value,
                provenance=(candidate.candidate_id, sha256(graph)),
                next_action="validate artifact independently before activation",
            )
        )
    return result


def ledger_events(events: list[tuple[str, dict[str, Any]]]) -> list[LedgerEvent]:
    rendered: list[LedgerEvent] = []
    parent_hash: str | None = None
    for sequence, (event_type, payload) in enumerate(events):
        body = {
            "sequence": sequence,
            "event_type": event_type,
            "payload": payload,
            "parent_hash": parent_hash,
        }
        event_hash = sha256(body)
        event = LedgerEvent(
            sequence=sequence,
            event_type=event_type,
            payload=payload,
            parent_hash=parent_hash,
            event_hash=event_hash,
        )
        rendered.append(event)
        parent_hash = event_hash
    return rendered


def run(
    context: dict[str, Any],
    *,
    generations: int = 3,
    toroidal_generations: int = 2,
    poles: int = 8,
) -> dict[str, Any]:
    graph = normalize(context)
    unlock_payload = result_payload(calculate_unlocks(context))
    system_discovery = discover(context)
    polycentric = polycentric_frontier(context, generations=max(1, generations))
    toroidal = toroidal_run(
        context,
        generations=max(1, toroidal_generations),
        pole_count=poles,
    )

    assets = [Asset(**item) for item in graph["assets"]]
    routes = [AcquisitionRoute(**item) for item in graph["acquisition_routes"]]

    reverse_engineering = [
        reverse_engineer(asset, routes)
        for asset in assets
    ]

    candidates: list[ValueCandidate] = []
    parent_ids: tuple[str, ...] = ()
    for generation in range(max(1, generations)):
        candidate = make_candidate(
            context,
            graph,
            unlock_payload,
            generation=generation,
            parent_ids=parent_ids,
        )
        candidates.append(candidate)
        parent_ids = (candidate.candidate_id,)

    frontier = pareto_frontier(candidates)
    loot = [
        artifact
        for candidate in frontier
        for artifact in loot_from_candidate(candidate, graph)
    ]

    route_plan = legal_routes(routes, {asset.asset_id for asset in assets})
    gates = [authority_gate(context, candidate) for candidate in frontier]

    event_pairs: list[tuple[str, dict[str, Any]]] = [
        ("value_graph_normalized", graph),
        ("unlock_calculated", unlock_payload),
        ("reverse_engineering_observed", {"items": reverse_engineering}),
        ("polycentric_frontier_generated", {"meta_sha256": polycentric["meta_architecture_sha256"]}),
        ("toroidal_frontier_generated", {"sha256": toroidal["toroidal_architecture_sha256"]}),
        ("pareto_frontier_selected", {"candidate_ids": [x.candidate_id for x in frontier]}),
        ("lawful_acquisition_filtered", {"route_ids": [x.route_id for x in route_plan]}),
        ("authority_gates_calculated", {"gates": gates}),
    ]
    ledger = ledger_events(event_pairs)

    result = {
        "version": VERSION,
        "generated_at": now(),
        "activation_state": ACTIVATION_STATE,
        "principle": (
            "maximize durable, reusable, evidence-aware value while keeping "
            "unknowns, proposals, authorization, and activation distinct"
        ),
        "value_graph": graph,
        "unlock": unlock_payload,
        "system_discovery": system_discovery,
        "polycentric_frontier": polycentric,
        "toroidal_frontier": toroidal,
        "reverse_engineering": reverse_engineering,
        "candidates": [asdict(candidate) for candidate in candidates],
        "pareto_frontier": [asdict(candidate) for candidate in frontier],
        "loot_inventory": [asdict(artifact) for artifact in loot],
        "lawful_acquisition_routes": [asdict(route) for route in route_plan],
        "authority_gates": gates,
        "ledger": [asdict(event) for event in ledger],
        "invariants": [
            "DECLARED != CALCULATED != EFFECTIVE",
            "CLAIMED != MEASURED != REPLICATED != EXPLAINED",
            "PROVENANCE != TRUTH",
            "UNKNOWN != permission",
            "PROPOSED != VERIFIED",
            "reverse_engineering != unauthorized access",
            "acquisition plan != acquisition execution",
            "proposal != activation",
            "bounded recursion != infinite execution",
        ],
    }
    digest_material = dict(result)
    digest_material.pop("generated_at", None)
    result["recursive_value_architecture_sha256"] = sha256(digest_material)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the EVEZ recursive value architecture engine."
    )
    parser.add_argument("context", help="JSON context file")
    parser.add_argument("--mode", choices=("scan", "evolve"), default="evolve")
    parser.add_argument("--generations", type=int, default=3)
    parser.add_argument("--toroidal-generations", type=int, default=2)
    parser.add_argument("--poles", type=int, default=8)
    parser.add_argument("--output")
    parser.add_argument("--ledger")
    args = parser.parse_args()

    context = json.loads(Path(args.context).read_text(encoding="utf-8"))

    if args.mode == "scan":
        graph = normalize(context)
        unlock = result_payload(calculate_unlocks(context))
        discovery = discover(context)
        result = {
            "version": VERSION,
            "activation_state": ACTIVATION_STATE,
            "value_graph": graph,
            "unlock": unlock,
            "system_discovery": discovery,
        }
        result["recursive_value_architecture_sha256"] = sha256(result)
    else:
        result = run(
            context,
            generations=max(1, args.generations),
            toroidal_generations=max(1, args.toroidal_generations),
            poles=max(3, min(32, args.poles)),
        )

    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    if args.ledger:
        ledger_lines = "\n".join(
            json.dumps(event, sort_keys=True)
            for event in result.get("ledger", [])
        )
        Path(args.ledger).write_text(ledger_lines + ("\n" if ledger_lines else ""), encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
