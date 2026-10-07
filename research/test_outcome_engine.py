from research.outcome_engine import compile_outcome

build = compile_outcome("build the missing temporal continuity layer")
assert build["outcome"]["action_class"] == "BUILD"
assert build["outcome"]["requires_authorization"] is False
assert len(build["outcome"]["stages"]) >= 6

merge = compile_outcome("finish and merge the verified implementation")
assert merge["outcome"]["action_class"] == "CONSEQUENTIAL"
assert merge["outcome"]["requires_authorization"] is True

assert len(build["outcome_sha256"]) == 64
print("outcome engine tests: PASS")
