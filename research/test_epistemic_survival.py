#!/usr/bin/env python3
from epistemic_survival import run
result = run()
assert result["scenario_count"] == 7
assert result["all_expected_outcomes_match"] is True
assert result["survival_score"] == 1.0
assert len(result["result_sha256"]) == 64
print("epistemic survival corpus test: PASS")
