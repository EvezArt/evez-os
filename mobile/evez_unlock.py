#!/usr/bin/env python3
"""Deterministic capability calculation and unlock engine for EVEZ-OS."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any


class Truth(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class UnlockState(StrEnum):
    UNLOCKED = "UNLOCKED"
    LOCKED = "LOCKED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Calculation:
    calculation_id: str
    operator: str
    inputs: tuple[str, ...]
    values: tuple[Any, ...]
    result: Truth
    reason: str


@dataclass(frozen=True)
class Capability:
    capability_id: str
    description: str
    requires: tuple[dict[str, Any], ...] = ()
    any_of: tuple[dict[str, Any], ...] = ()
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class CapabilityResult:
    capability_id: str
    state: UnlockState
    calculations: tuple[Calculation, ...]
    dependencies: tuple[dict[str, Any], ...]
    unlock_score: float
    unlock_sha256: str
    reason: str


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _get(ctx: dict[str, Any], path: str) -> tuple[bool, Any]:
    current: Any = ctx
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _calculate(predicate: dict[str, Any], ctx: dict[str, Any], prefix: str) -> Calculation:
    operator = str(predicate.get("op", "exists"))
    inputs = tuple(str(x) for x in predicate.get("inputs", ()))
    values = []
    for item in inputs:
        found, value = _get(ctx, item)
        values.append(value if found else None)

    if operator == "exists":
        result = Truth.PASS if values and values[0] is not None else Truth.UNKNOWN
        reason = "input exists" if result == Truth.PASS else "required input is absent"
    elif operator in {"eq", "neq", "gt", "gte", "lt", "lte", "in"}:
        if not inputs or any(v is None for v in values):
            result, reason = Truth.UNKNOWN, "one or more calculation inputs are unknown"
        else:
            left = values[0]
            target = predicate.get("value")
            try:
                if operator == "eq":
                    ok = left == target
                elif operator == "neq":
                    ok = left != target
                elif operator == "gt":
                    ok = left > target
                elif operator == "gte":
                    ok = left >= target
                elif operator == "lt":
                    ok = left < target
                elif operator == "lte":
                    ok = left <= target
                else:
                    ok = left in target
            except (TypeError, ValueError):
                result, reason = Truth.UNKNOWN, "calculation operands are incompatible"
            else:
                result = Truth.PASS if ok else Truth.FAIL
                reason = f"{inputs[0]} {operator} {target!r}"
    elif operator == "is_true":
        value = values[0] if values else None
        result = Truth.PASS if value is True else Truth.FAIL if value is False else Truth.UNKNOWN
        reason = f"{inputs[0]} == true"
    elif operator == "is_false":
        value = values[0] if values else None
        result = Truth.PASS if value is False else Truth.FAIL if value is True else Truth.UNKNOWN
        reason = f"{inputs[0]} == false"
    elif operator in {"all", "any"}:
        children = predicate.get("predicates", [])
        child_results = [_calculate(child, ctx, f"{prefix}.{i}") for i, child in enumerate(children)]
        values = [child.result.value for child in child_results]
        if operator == "all":
            result = Truth.FAIL if Truth.FAIL.value in values else Truth.UNKNOWN if Truth.UNKNOWN.value in values else Truth.PASS
        else:
            result = Truth.PASS if Truth.PASS.value in values else Truth.UNKNOWN if Truth.UNKNOWN.value in values else Truth.FAIL
        reason = f"{operator}({', '.join(values)})"
    elif operator == "not":
        child = _calculate(predicate["predicate"], ctx, f"{prefix}.not")
        result = Truth.FAIL if child.result == Truth.PASS else Truth.PASS if child.result == Truth.FAIL else Truth.UNKNOWN
        values = [child.result.value]
        reason = f"not({child.result.value})"
    elif operator == "score_gte":
        path = str(predicate.get("score", ""))
        found, score = _get(ctx, path)
        threshold = float(predicate.get("value", 0))
        values = [score]
        if not found or score is None:
            result, reason = Truth.UNKNOWN, f"{path} is unknown"
        else:
            result = Truth.PASS if float(score) >= threshold else Truth.FAIL
            reason = f"{path} >= {threshold}"
    else:
        result, reason = Truth.UNKNOWN, f"unsupported calculation operator: {operator}"

    return Calculation(
        calculation_id=_hash({"prefix": prefix, "predicate": predicate, "values": values})[:20],
        operator=operator,
        inputs=inputs,
        values=tuple(values),
        result=result,
        reason=reason,
    )


def evaluate_capability(
    capability: Capability,
    ctx: dict[str, Any],
    cache: dict[str, CapabilityResult],
) -> CapabilityResult:
    dependencies = []
    for dependency in capability.depends_on:
        prior = cache.get(dependency)
        state = prior.state if prior else UnlockState.UNKNOWN
        dependencies.append({"capability_id": dependency, "state": state.value})
        if state == UnlockState.LOCKED:
            reason = f"dependency {dependency} is locked"
            return _result(capability, UnlockState.LOCKED, (), dependencies, 0.0, reason)
        if state == UnlockState.UNKNOWN:
            reason = f"dependency {dependency} is unknown"
            return _result(capability, UnlockState.UNKNOWN, (), dependencies, 0.0, reason)

    calculations = [
        _calculate(predicate, ctx, f"{capability.capability_id}.requires.{i}")
        for i, predicate in enumerate(capability.requires)
    ]
    alternatives = [
        _calculate(predicate, ctx, f"{capability.capability_id}.any.{i}")
        for i, predicate in enumerate(capability.any_of)
    ]
    calculations.extend(alternatives)

    required = [c.result for c in calculations[: len(capability.requires)]]
    any_results = [c.result for c in alternatives]

    required_unknown = Truth.UNKNOWN in required
    required_fail = Truth.FAIL in required
    alternatives_fail = bool(capability.any_of) and Truth.PASS not in any_results
    alternatives_unknown = bool(capability.any_of) and Truth.UNKNOWN in any_results

    if required_fail:
        state, reason = UnlockState.LOCKED, "required calculation failed"
    elif required_unknown:
        state, reason = UnlockState.UNKNOWN, "required calculation is unknown"
    elif alternatives_fail and not alternatives_unknown:
        state, reason = UnlockState.LOCKED, "no alternative unlock calculation passed"
    elif alternatives_fail:
        state, reason = UnlockState.UNKNOWN, "alternative unlock calculation is unknown"
    else:
        state, reason = UnlockState.UNLOCKED, "all required calculations passed"

    known = [c for c in calculations if c.result != Truth.UNKNOWN]
    score = round(sum(c.result == Truth.PASS for c in known) / len(known), 4) if known else 0.0
    return _result(capability, state, tuple(calculations), dependencies, score, reason)


def _result(
    capability: Capability,
    state: UnlockState,
    calculations: tuple[Calculation, ...],
    dependencies: list[dict[str, Any]],
    score: float,
    reason: str,
) -> CapabilityResult:
    canonical = {
        "capability_id": capability.capability_id,
        "state": state.value,
        "calculations": [asdict(c) for c in calculations],
        "dependencies": dependencies,
        "unlock_score": score,
        "reason": reason,
    }
    return CapabilityResult(
        capability.capability_id,
        state,
        calculations,
        tuple(dependencies),
        score,
        _hash(canonical),
        reason,
    )


DEFAULT_CAPABILITIES = (
    Capability("observe.local", "Read local system state.",
               requires=({"op": "is_true", "inputs": ("device.present",)},)),
    Capability("witness.write", "Append a local witness event.",
               requires=(
                   {"op": "eq", "inputs": ("evidence.chain_status",), "value": "VERIFIED"},
                   {"op": "is_true", "inputs": ("storage.writable",)},
               ), depends_on=("observe.local",)),
    Capability("evidence.sync", "Synchronize verified local evidence.",
               requires=(
                   {"op": "eq", "inputs": ("evidence.chain_status",), "value": "VERIFIED"},
                   {"op": "is_true", "inputs": ("network.available",)},
                   {"op": "is_true", "inputs": ("sync.endpoint_configured",)},
               ), depends_on=("witness.write",)),
    Capability("pipeline.run", "Execute a normal EVEZ pipeline cycle.",
               requires=(
                   {"op": "is_true", "inputs": ("runtime.healthy",)},
                   {"op": "eq", "inputs": ("evidence.chain_status",), "value": "VERIFIED"},
               ), depends_on=("observe.local",)),
    Capability("self.modify", "Apply a self-modifying operation.",
               requires=(
                   {"op": "eq", "inputs": ("authorization.state",), "value": "AUTHORIZED"},
                   {"op": "is_true", "inputs": ("rollback.available",)},
                   {"op": "is_true", "inputs": ("tests.passed",)},
                   {"op": "eq", "inputs": ("evidence.chain_status",), "value": "VERIFIED"},
               ), depends_on=("pipeline.run",)),
    Capability("deploy.remote", "Deploy an already-validated operation.",
               requires=(
                   {"op": "eq", "inputs": ("authorization.state",), "value": "AUTHORIZED"},
                   {"op": "is_true", "inputs": ("rollback.available",)},
                   {"op": "is_true", "inputs": ("tests.passed",)},
                   {"op": "is_true", "inputs": ("network.available",)},
                   {"op": "is_true", "inputs": ("artifact.provenance_complete",)},
               ), depends_on=("pipeline.run",)),
    Capability("voice.render", "Render a local machine-voice artifact.",
               requires=(
                   {"op": "is_true", "inputs": ("runtime.healthy",)},
                   {"op": "is_true", "inputs": ("voice.model_available",)},
               ), depends_on=("observe.local",)),
    Capability("music.render", "Render a local generated music artifact.",
               requires=(
                   {"op": "is_true", "inputs": ("runtime.healthy",)},
                   {"op": "is_true", "inputs": ("music.engine_available",)},
               ), depends_on=("observe.local",)),
    Capability("autonomous.execute", "Execute an autonomous action after safety predicates pass.",
               requires=(
                   {"op": "eq", "inputs": ("authorization.state",), "value": "AUTHORIZED"},
                   {"op": "is_true", "inputs": ("rollback.available",)},
                   {"op": "is_true", "inputs": ("tests.passed",)},
                   {"op": "eq", "inputs": ("evidence.chain_status",), "value": "VERIFIED"},
               ), any_of=(
                   {"op": "is_true", "inputs": ("policy.explicit_allow",)},
                   {"op": "eq", "inputs": ("execution.mode",), "value": "DRY_RUN"},
               ), depends_on=("pipeline.run",)),
)


def calculate_unlocks(ctx: dict[str, Any]) -> dict[str, CapabilityResult]:
    cache: dict[str, CapabilityResult] = {}
    pending = list(DEFAULT_CAPABILITIES)
    while pending:
        progressed = False
        for capability in pending[:]:
            if all(dep in cache for dep in capability.depends_on):
                cache[capability.capability_id] = evaluate_capability(capability, ctx, cache)
                pending.remove(capability)
                progressed = True
        if not progressed:
            break
    return cache


def result_payload(results: dict[str, CapabilityResult]) -> dict[str, Any]:
    capabilities = [asdict(result) for result in results.values()]
    payload = {
        "version": "evez-capability-unlock/v1",
        "unlocked": [x["capability_id"] for x in capabilities if x["state"] == "UNLOCKED"],
        "locked": [x["capability_id"] for x in capabilities if x["state"] == "LOCKED"],
        "unknown": [x["capability_id"] for x in capabilities if x["state"] == "UNKNOWN"],
        "capabilities": capabilities,
    }
    payload["calculation_sha256"] = _hash(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate EVEZ-OS capability unlocks.")
    parser.add_argument("context", help="JSON context file, or '-' for stdin")
    args = parser.parse_args()
    payload = result_payload(calculate_unlocks(json.load(sys.stdin) if args.context == "-" else json.loads(Path(args.context).read_text())))
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
