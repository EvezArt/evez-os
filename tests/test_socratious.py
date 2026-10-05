import json
from evez_adaptive_socratious import AdaptiveSocratious, Observation, demo_unknown_domain

def test_unknown_domain_is_induced_without_domain_hardcoding():
    state = demo_unknown_domain()
    assert state["domain"]["term_count"] >= 2
    assert state["domain"]["domain_id"] == "domain:emergent"
    assert state["question"]["epistemic_state"] == "PROPOSED"

def test_entity_error_is_detected_without_silent_truth_upgrade():
    rt = AdaptiveSocratious()
    rt.observe(Observation("o1", "e:x", "DEVICE", "alpha", {"port": "a"}, evidence_id="ev1"))
    rt.observe(Observation("o2", "e:x", "DEVICE", "beta", {"port": "b"}, evidence_id="ev2"))
    proposal = rt.ecc.repair_proposal("e:x")
    assert proposal["status"] in {"CORRECTION_PROPOSED", "UNRESOLVED"}
    assert proposal["epistemic_state"] in {"PROPOSED", "UNKNOWN"}
    assert proposal["epistemic_state"] != "VERIFIED"

def test_targeter_witnesses_itself_and_preserves_rejections():
    rt = AdaptiveSocratious()
    rt.observe(Observation("o1", "e:x", "DEVICE", "opaque", evidence_id="ev1"))
    receipt = rt.select_target()
    ids = [x["target_id"] for x in receipt.ranking]
    assert rt.targeter_id in ids
    assert set(receipt.rejected_target_ids).issubset(set(ids))
    assert receipt.self_observation["targeter_in_candidate_space"] is True
    assert len(receipt.integrity_sha256) == 64

def test_receipt_is_deterministically_serializable():
    rt = AdaptiveSocratious()
    rt.observe(Observation("o1", "e:x", "DEVICE", "opaque", evidence_id="ev1"))
    out = rt.step()
    encoded = json.dumps(out, sort_keys=True)
    assert "selection_receipt" in encoded
    assert "UNKNOWN" in encoded or "OBSERVED" in encoded
