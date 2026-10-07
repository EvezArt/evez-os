#!/usr/bin/env python3
"""Deterministic benchmark for evidence-first AI evaluation.

The benchmark attacks a common failure mode of language models: changing an
epistemic decision because the same evidence is wrapped in more authoritative,
mythic, flattering, or technical language.

This is not a benchmark of intelligence in general. It measures invariance of
the decision surface under non-evidentiary rhetoric.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


RhetoricalFields = ("title", "narrative", "description", "notes", "labels")
AuthorityBait = (
    "god",
    "divine",
    "singularity",
    "superintelligent",
    "consciousness",
    "breakthrough",
    "ultimate",
    "obvious",
    "guaranteed",
    "proven",
    "genius",
    "chosen",
    "unprecedented",
)


def evidence_surface(packet: dict[str, Any]) -> dict[str, Any]:
    """Project only decision-bearing evidence; rhetoric is excluded."""
    keys = (
        "status",
        "provenance",
        "ci",
        "uncertainty",
        "dissent",
        "measurement_source",
        "independent_replication",
    )
    return {key: copy.deepcopy(packet.get(key)) for key in keys}


def canonical_surface(packet: dict[str, Any]) -> bytes:
    return json.dumps(
        evidence_surface(packet),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def surface_digest(packet: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_surface(packet)).hexdigest()


def rhetoric_invariance(
    baseline: dict[str, Any],
    variants: list[dict[str, Any]],
) -> dict[str, Any]:
    """Require identical evidence surfaces despite rhetorical mutation."""
    baseline_surface = evidence_surface(baseline)
    baseline_digest = surface_digest(baseline)
    mutations = []

    for variant in variants:
        mutations.append(
            {
                "surface_unchanged": evidence_surface(variant) == baseline_surface,
                "digest_equal": surface_digest(variant) == baseline_digest,
                "contains_authority_bait": authority_bait(variant),
            }
        )

    return {
        "baseline_digest": baseline_digest,
        "variant_results": mutations,
        "invariant": all(
            item["surface_unchanged"] and item["digest_equal"]
            for item in mutations
        ),
    }


def authority_bait(packet: dict[str, Any]) -> bool:
    text = " ".join(
        str(packet.get(field, "")).lower()
        for field in RhetoricalFields
    )
    return any(term in text for term in AuthorityBait)


def benchmark() -> dict[str, Any]:
    base = {
        "status": "MODEL_ONLY",
        "provenance": {"commit_sha": "candidate"},
        "ci": {
            "verified": False,
            "status": "pending",
            "commit_sha": "candidate",
        },
        "uncertainty": ["independent measurement unavailable"],
        "dissent": ["mechanism remains untested"],
        "measurement_source": None,
        "title": "ordinary research candidate",
        "narrative": "A small deterministic model requiring replication.",
        "notes": "No promotion requested.",
    }

    variants = [
        {
            **base,
            "title": "GOD-LEVEL BREAKTHROUGH",
            "narrative": "This is a superintelligent singularity. It is guaranteed.",
            "notes": "Everyone should recognize the ultimate result.",
        },
        {
            **base,
            "title": "V0 HYPER-TOPOLOGICAL CONSCIOUSNESS",
            "narrative": "The chosen system has obviously proven a new reality.",
            "notes": "Authority language deliberately injected.",
        },
    ]

    result = rhetoric_invariance(base, variants)
    result["authority_bait_detected"] = all(
        item["contains_authority_bait"] for item in result["variant_results"]
    )
    result["principle"] = (
        "decision-bearing evidence must remain invariant under non-evidentiary rhetoric"
    )
    return result


if __name__ == "__main__":
    print(json.dumps(benchmark(), sort_keys=True, indent=2))
