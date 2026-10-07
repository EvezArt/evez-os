#!/usr/bin/env python3
from __future__ import annotations

from research.intent_optimizer import optimize_intent, score_vector, vectorize


precise = vectorize("verify the release artifact against the published checksum")
assert 0.0 <= precise.clarity <= 1.0
assert 0.0 <= score_vector(precise) <= 1.0

blocked = optimize_intent(["do it"])
assert blocked["status"] == "REQUIRES_SPECIFICATION"

gap = optimize_intent(["build a reproducible verifier"])
assert gap["status"] == "EVIDENCE_GAP"

ranked = optimize_intent([
    "verify the release artifact against the published checksum",
    "deploy the release artifact",
])
assert ranked["candidate_count"] == 2
assert ranked["best"]["intent"] in {
    "verify the release artifact against the published checksum",
    "deploy the release artifact",
}

tie = optimize_intent([
    "verify artifact checksum",
    "verify artifact hash",
], tie_margin=1.0)
assert tie["status"] == "AMBIGUOUS_TIE"

print("intent optimizer tests: PASS")
