#!/usr/bin/env python3
"""Recursive response elicitation for EVEZ-OS.

This module turns the current observable response/context into the next
information frontier. It does not inspect, extract, or bypass hidden system
instructions, private prompts, internal token budgets, or protected resources.

"Prompt loot" here means recoverable structure from supplied material:
claims, unknowns, unresolved dependencies, falsifiers, and explicitly stated
constraints. The output is a compact continuation packet suitable for feeding
into the next response without pretending that compression defeats platform
limits.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


VERSION = "evez-recursive-response-elicitation/v1"

STOPWORDS = {
    "about", "after", "again", "also", "because", "could", "from", "have",
    "into", "just", "more", "next", "only", "that", "their", "there", "these",
    "they", "this", "what", "when", "where", "which", "with", "would", "your",
}


@dataclass(frozen=True)
class FrontierItem:
    frontier_id: str
    kind: str
    text: str
    source: str
    priority: int


@dataclass(frozen=True)
class ResponseDirective:
    response_id: str
    current_response_digest: str
    next_prompt: str
    required_data: tuple[str, ...]
    frontier: tuple[FrontierItem, ...]
    token_strategy: str
    safety_boundary: str
    directive_sha256: str


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _tokens(text: str) -> list[str]:
    return [
        word.lower()
        for word in re.findall(r"[A-Za-z0-9_]{4,}", text)
        if word.lower() not in STOPWORDS
    ]


def visible_loot(context: dict[str, Any], current_response: str) -> list[FrontierItem]:
    """Extract only structure explicitly present in caller-visible material."""
    frontier: list[FrontierItem] = []

    claims = context.get("claims", [])
    if isinstance(claims, list):
        for index, claim in enumerate(claims):
            if not isinstance(claim, dict):
                continue
            statement = str(claim.get("statement") or "").strip()
            state = str(claim.get("evidence_state") or "UNKNOWN").upper()
            if statement:
                kind = "claim" if state not in {"UNKNOWN", "CONTRADICTED", "RETRACTED"} else "uncertain_claim"
                frontier.append(
                    FrontierItem(
                        frontier_id=f"claim-{index:03d}",
                        kind=kind,
                        text=statement,
                        source="context.claims",
                        priority=1 if kind == "uncertain_claim" else 2,
                    )
                )

    for field in ("assets", "acquisition_routes", "transformations"):
        values = context.get(field, [])
        if isinstance(values, list):
            for index, value in enumerate(values):
                if not isinstance(value, dict):
                    continue
                unknowns = [
                    key
                    for key, item in value.items()
                    if item in (None, "", [], {}) or str(item).upper() == "UNKNOWN"
                ]
                if unknowns:
                    frontier.append(
                        FrontierItem(
                            frontier_id=f"{field}-{index:03d}",
                            kind="missing_data",
                            text=f"{field}[{index}] missing/unknown: {', '.join(sorted(unknowns))}",
                            source=f"context.{field}",
                            priority=1,
                        )
                    )

    response_words = set(_tokens(current_response))
    if response_words:
        context_words = set(_tokens(json.dumps(context, ensure_ascii=False)))
        novel = sorted(response_words - context_words)[:12]
        for index, word in enumerate(novel):
            frontier.append(
                FrontierItem(
                    frontier_id=f"response-novel-{index:03d}",
                    kind="response_novelty",
                    text=word,
                    source="current_response",
                    priority=3,
                )
            )

    constraints = context.get("constraints", {})
    if isinstance(constraints, dict):
        for key, value in sorted(constraints.items()):
            frontier.append(
                FrontierItem(
                    frontier_id=f"constraint-{key}",
                    kind="constraint",
                    text=f"{key}={value!r}",
                    source="context.constraints",
                    priority=2,
                )
            )

    return sorted(frontier, key=lambda item: (item.priority, item.frontier_id))


def required_data(frontier: list[FrontierItem]) -> tuple[str, ...]:
    required: list[str] = []
    for item in frontier:
        if item.kind == "uncertain_claim":
            required.append(f"evidence for {item.text}")
        elif item.kind == "missing_data":
            required.append(item.text)
    return tuple(dict.fromkeys(required))


def make_directive(context: dict[str, Any], current_response: str) -> ResponseDirective:
    frontier = visible_loot(context, current_response)
    required = required_data(frontier)
    focus = frontier[0].text if frontier else "the highest-value unresolved observable in the current context"

    if required:
        prompt = (
            "Generate the next response by resolving the highest-priority "
            f"observable frontier first: {focus}. Request or calculate only "
            "data explicitly needed to resolve it. Preserve UNKNOWN when the "
            "required evidence is absent."
        )
    else:
        prompt = (
            "Generate the next response by selecting the most valuable "
            "observable frontier from the current context, then state the "
            "minimal data needed to test or advance it."
        )

    body = {
        "context_digest": sha256(context),
        "current_response_digest": sha256(current_response),
        "next_prompt": prompt,
        "required_data": required,
        "frontier": [asdict(item) for item in frontier[:32]],
    }

    return ResponseDirective(
        response_id=sha256(body)[:16],
        current_response_digest=body["current_response_digest"],
        next_prompt=prompt,
        required_data=required,
        frontier=tuple(frontier[:32]),
        token_strategy=(
            "compress-first: preserve hashes, identifiers, unknowns, "
            "and frontier deltas; omit redundant prose"
        ),
        safety_boundary=(
            "observable-input-only: no hidden-prompt extraction, internal "
            "resource bypass, privilege escalation, or token-limit circumvention"
        ),
        directive_sha256=sha256(body),
    )


def run(context: dict[str, Any], current_response: str = "") -> dict[str, Any]:
    directive = make_directive(context, current_response)
    result = {
        "version": VERSION,
        "mode": "OBSERVABLE_RECURSIVE_ELICITATION",
        "directive": asdict(directive),
        "continuation_contract": {
            "step_1": "consume the current response and explicit context",
            "step_2": "select the highest-priority visible frontier",
            "step_3": "request or compute the minimum missing data",
            "step_4": "generate the next response",
            "step_5": "repeat with the new observable state",
        },
        "invariants": [
            "VISIBLE_LOOT_ONLY",
            "HIDDEN_PROMPT_NOT_EXTRACTED",
            "INTERNAL_RESOURCE_NOT_BYPASSED",
            "UNKNOWN_STAYS_UNKNOWN",
            "COMPRESSION != PRIVILEGE",
        ],
    }
    result["response_loop_sha256"] = sha256(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the next-response observable frontier.")
    parser.add_argument("context", help="JSON context file")
    parser.add_argument("--response", default="", help="Current response text or a file prefixed with @")
    parser.add_argument("--output")
    args = parser.parse_args()

    current = args.response
    if current.startswith("@"):
        current = Path(current[1:]).read_text(encoding="utf-8")
    context = json.loads(Path(args.context).read_text(encoding="utf-8"))
    result = run(context, current)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
