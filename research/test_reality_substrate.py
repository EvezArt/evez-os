# SPDX-License-Identifier: MIT
#!/usr/bin/env python3
from research.reality_substrate import (
    AppendOnlyLedger,
    CausalEvent,
    CulturalUnit,
    DirectorCandidate,
    ProjectionSpec,
    SelfMetric,
    WorldEntity,
    WorldSnapshot,
    branch_counterfactual,
    choose_next_operation,
    compile_projection,
    evaluate_self,
    snapshot_digest,
    transmit_unit,
)

entity = WorldEntity(
    entity_id="mount:001", entity_type="terrain", state="ACTIVE",
    attributes={"elevation_m": 1200, "age_years": 40000},
    epistemic_state="PROPOSED",
)
event = CausalEvent(
    event_id="evt:001", timestamp="2026-10-07T20:00:00Z",
    kind="OBSERVATION", actor_id="operator", causes=(), effects=("mount:001",),
    payload={"weathered": False}, evidence=("obs:001",), epistemic_state="OBSERVED",
)
snapshot = WorldSnapshot(
    snapshot_id="snap:001", timestamp="2026-10-07T20:00:00Z",
    parent_snapshot=None, entities=(entity,), events=(event,),
)
assert len(snapshot_digest(snapshot)) == 64

spec = ProjectionSpec(
    projection_id="proj:001", representation="THREE_D",
    observer_id="observer:001", snapshot_id="snap:001",
    parameters={"style": "scientific"},
)
manifest = compile_projection(snapshot, spec)
assert manifest.reproducible is True
assert manifest.source_event_ids == ("evt:001",)
assert manifest.epistemic_state == "PROPOSED"

ledger = AppendOnlyLedger()
ledger.append({"type": "OBSERVED_FACT", "payload": {"value": 1}})
ledger.append({"type": "STATE_TRANSITION", "payload": {"value": 2}})
ledger.verify()
assert ledger.replay()[1]["payload"]["value"] == 2

hypothesis = CausalEvent(
    event_id="hyp:001", timestamp="2026-10-07T20:01:00Z",
    kind="HYPOTHESIS", actor_id="operator", causes=("evt:001",), effects=(),
    payload={"rainfall_mm": 5000}, epistemic_state="PROPOSED",
)
branch = branch_counterfactual(snapshot, hypothesis, "branch:rainfall")
assert branch.label == "SIMULATED"

culture = CulturalUnit(
    unit_id="cult:root", parent_ids=(), carrier="EVEZ",
    payload={"symbol": "⧢⦟⧢⥋"}, mutation_index=0,
)
child = transmit_unit(culture, "agent:02", {"style": "minimal"})
assert child.parent_ids == ("cult:root",)
assert child.mutation_index == 1
assert child.transmission_count == 1

metric = SelfMetric(
    metric_id="metric:001", operation_id="verify:001",
    predicted=0.8, observed=0.6, resource_cost=2.0,
    timestamp="2026-10-07T20:02:00Z",
)
evaluation = evaluate_self(metric)
assert evaluation["absolute_error"] == 0.2
assert 0 < evaluation["efficiency"] < 1

choice = choose_next_operation([
    DirectorCandidate("cheap", 2, 1, 0.0, 1.0),
    DirectorCandidate("risky", 10, 10, 1.0, 5.0),
])
assert choice["status"] == "SELECTED"
assert choice["selected"]["operation_id"] == "cheap"
assert choice["success_criterion_locked"] is True
assert choice["self_authorization"] is False

print("reality substrate tests: PASS")
