# SPDX-License-Identifier: MIT
#!/usr/bin/env python3
from research.artifact_contracts import (
    build_evez, build_evex, verify_evez, verify_evex
)

evez = build_evez(
    artifact_id="world:snap:001",
    artifact_type="WORLD_SNAPSHOT",
    state="PROPOSED",
    body={"entities": []},
    provenance=("evt:001",),
)
assert verify_evez(evez)["verified"] is True
tampered = dict(evez)
tampered["body"] = {"entities": [{"id": "changed"}]}
assert verify_evez(tampered)["verified"] is False

evex = build_evex(
    envelope_id="evex:001",
    action="VERIFY",
    sender="evez",
    payload={"artifact_id": "world:snap:001"},
    correlation_id="op:001",
    authorization_required=False,
    provenance=("world:snap:001",),
)
assert verify_evex(evex)["verified"] is True

try:
    build_evex(
        envelope_id="evex:bad",
        action="ACT",
        sender="evez",
        payload={},
        correlation_id="op:002",
        authorization_required=False,
    )
except ValueError:
    pass
else:
    raise AssertionError("ACT must require explicit authorization")

print("artifact contract tests: PASS")
