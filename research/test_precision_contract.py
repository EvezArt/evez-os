from research.precision_contract import compile_from_intent, validate_spec

sloppy = compile_from_intent("do everything fully and make it better")
assert sloppy["status"] == "REQUIRES_SPECIFICATION"
assert sloppy["vague_terms"]

precise = validate_spec({
    "subject": "evez-os branch evez-weather-mycelial-flux/2026-10",
    "action": "add deterministic precision validation",
    "scope": "research and mobile operator surfaces only",
    "inputs": ["intent text", "repository files"],
    "constraints": ["offline-safe", "no automatic consequential actions"],
    "evidence": ["unit tests", "CI run"],
    "acceptance": "test exit code 0 and resulting spec hash is 64 hex characters",
    "time": "single bounded execution cycle",
    "authority": "repository write authority only",
})
assert precise["valid"] is True

missing = validate_spec({"subject": "repo", "action": "build"})
assert missing["valid"] is False
assert any(row["code"] == "MISSING_FIELD" for row in missing["findings"])

print("precision contract tests: PASS")
