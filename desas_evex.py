"""DESA-S -> EVEX bridge.

Converts one deterministic DESA-S state snapshot into an EVEX accountable
state-transition artifact. The bridge carries observable state, selection
receipts, and epistemic classification. It does not confer authority or
execute payloads.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any

def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")

def digest(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()

def build_evex_transition(state: dict[str, Any]) -> dict[str, Any]:
    question = state["question"]
    receipt = state["selection_receipt"]
    adaptation = {
        "profile": "desas-s.v1",
        "domain_state_hash": digest(state["domain"]),
        "sme_profile_hash": digest(state["sme"]),
        "selection_receipt_hash": receipt["integrity_sha256"],
        "question_id": question["question_id"],
        "target_id": question["target_id"],
    }
    transition = {
        "parent_state_hash": state["parent_state_hash"],
        "classification": {
            "state": question["epistemic_state"],
            "basis": [receipt["receipt_id"], question["question_id"]],
        },
        "authority": {
            "capability": "desas.socratious.reference",
            "policy": "desas-v1-local",
        },
        "action": {
            "type": "desas.propose_question",
            "input_hash": state["parent_state_hash"],
        },
        "acceptance": {
            "tests": [
                "self-target-present",
                "rejected-targets-preserved",
                "epistemic-no-promotion",
                "deterministic-selection-receipt",
            ],
        },
        "result": {
            "status": "SUCCEEDED",
            "observations": [
                question["question_id"],
                question["target_id"],
            ],
        },
        "new_state_hash": state["new_state_hash"],
        "adaptation": adaptation,
    }
    artifact = {
        "evex": "EVEX",
        "version": 1,
        "profile": "evez.exchange",
        "kind": "state.transition",
        "id": f"desas-transition:{state['new_state_hash'][:16]}",
        "transition": transition,
        "integrity": {"algorithm": "sha256", "sha256": None},
    }
    artifact["integrity"]["sha256"] = digest(artifact)
    return artifact

if __name__ == "__main__":
    from evez_adaptive_socratious import demo_unknown_domain
    print(json.dumps(build_evex_transition(demo_unknown_domain()), indent=2,
                     ensure_ascii=False, sort_keys=True))
