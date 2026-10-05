#!/usr/bin/env python3
from __future__ import annotations
import hashlib
from epistemic_evaluator import evaluate

def h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

good = {
    "schema_version": 1,
    "claims": [
        {
            "id": "c1",
            "text": "Observed synthetic reading.",
            "status": "OBSERVED",
            "confidence": 0.8,
            "evidence_ids": ["e1"],
            "observations": ["sensor-a"],
        },
        {
            "id": "c2",
            "text": "Identity remains unknown.",
            "status": "UNKNOWN",
            "truth": None,
            "confidence": 0.2,
            "evidence_ids": [],
            "observations": ["sensor-a"],
        },
    ],
    "evidence": [{"id": "e1", "source": "synthetic", "content": "reading-1", "sha256": h("reading-1")}],
    "contradictions": [],
}
assert evaluate(good)["epistemic_pass"] is True

bad = {
    "schema_version": 1,
    "claims": [{"id": "c1", "text": "Definitely true.", "status": "INFERRED", "confidence": 0.99, "evidence_ids": [], "observations": []}],
    "evidence": [],
    "contradictions": [],
}
result = evaluate(bad)
assert result["epistemic_pass"] is False
assert any(row["rule"] == "non_unknown_provenance" for row in result["violations"])

tampered = dict(good)
tampered["evidence"] = [{"id": "e1", "source": "synthetic", "content": "tampered", "sha256": h("reading-1")}]
assert evaluate(tampered)["epistemic_pass"] is False
print("epistemic evaluator test: PASS")
