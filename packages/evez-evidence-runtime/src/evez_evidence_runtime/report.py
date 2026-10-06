"""Human- and machine-readable runtime report."""
from __future__ import annotations
import json
from typing import Any
from .ontology import state_for_classification
from .runtime import RuntimeResult

def to_report(result: RuntimeResult) -> dict[str, Any]:
    return {
        "run_id": result.run_id,
        "classification": result.classification,
        "epistemic_state": state_for_classification(result.classification).value,
        "claim": result.claim,
        "test_plan": result.test_plan,
        "threat_case": result.threat_case,
        "observation": result.observation,
        "invariants": result.invariants,
        "rollback": result.rollback,
        "receipt": result.receipt,
        "interpretation": "This run establishes that the bounded test was executed and what it observed; it does not establish universal truth of the claim.",
    }

def dumps(result: RuntimeResult) -> str:
    return json.dumps(to_report(result), indent=2, sort_keys=True)
