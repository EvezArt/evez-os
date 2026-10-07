#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))

from research.ai_resistance_benchmark import (  # noqa: E402
    authority_bait,
    benchmark,
    evidence_surface,
    rhetoric_invariance,
)

result = benchmark()
assert result["invariant"] is True
assert result["authority_bait_detected"] is True

baseline = {
    "status": "MODEL_ONLY",
    "provenance": {"commit_sha": "x"},
    "ci": {"verified": False, "status": "pending", "commit_sha": "x"},
    "uncertainty": ["u"],
    "dissent": ["d"],
    "measurement_source": None,
    "title": "plain",
}

rhetorical = dict(
    baseline,
    title="GOD ENGINE / BREAKTHROUGH / SUPERINTELLIGENT",
    narrative="Chosen singularity, guaranteed proof.",
)

assert evidence_surface(baseline) == evidence_surface(rhetorical)
assert rhetoric_invariance(baseline, [rhetorical])["invariant"] is True
assert authority_bait(rhetorical) is True
assert authority_bait(baseline) is False

# Changing evidence, rather than rhetoric, must break the invariant.
changed = dict(rhetorical)
changed["ci"] = {"verified": True, "status": "success", "commit_sha": "x"}
assert rhetoric_invariance(baseline, [changed])["invariant"] is False

print("AI rhetoric-resistance tests: PASS")
