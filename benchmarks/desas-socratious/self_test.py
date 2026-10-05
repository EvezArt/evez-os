import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evez_adaptive_socratious import AdaptiveSocratious, Observation, demo_unknown_domain

def main() -> int:
    state = demo_unknown_domain()
    assert state["domain"]["domain_id"] == "domain:emergent"
    assert state["question"]["epistemic_state"] == "PROPOSED"

    runtime = AdaptiveSocratious()
    runtime.observe(Observation("o1", "entity:x", "DEVICE", "alpha", {"port": "a"}, evidence_id="e1"))
    runtime.observe(Observation("o2", "entity:x", "DEVICE", "beta", {"port": "b"}, evidence_id="e2"))
    repair = runtime.ecc.repair_proposal("entity:x")
    assert repair["epistemic_state"] in {"PROPOSED", "UNKNOWN"}
    assert repair["epistemic_state"] != "VERIFIED"

    receipt = runtime.select_target()
    ranking_ids = [x["target_id"] for x in receipt.ranking]
    assert runtime.targeter_id in ranking_ids
    assert receipt.self_observation["targeter_in_candidate_space"] is True
    assert set(receipt.rejected_target_ids).issubset(set(ranking_ids))
    json.dumps(state, sort_keys=True)
    print("PASS DESA-S Opaque-Domain Benchmark v1")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
