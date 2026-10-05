import json
from evez_adaptive_socratious import AdaptiveSocratious, Observation, demo_unknown_domain
from desas_evex import build_evex_transition, digest

def test_unknown_domain_is_induced_without_domain_hardcoding():
    state = demo_unknown_domain()
    assert state["domain"]["term_count"] >= 2
    assert state["domain"]["domain_id"] == "domain:emergent"
    assert state["question"]["epistemic_state"] == "PROPOSED"
    assert len(state["parent_state_hash"]) == 64
    assert len(state["new_state_hash"]) == 64
    assert state["parent_state_hash"] != state["new_state_hash"]

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

def test_evex_bridge_binds_adaptation_state():
    state = demo_unknown_domain()
    artifact = build_evex_transition(state)
    transition = artifact["transition"]
    assert artifact["evex"] == "EVEX"
    assert transition["adaptation"]["profile"] == "desas-s.v1"
    assert transition["classification"]["state"] == "PROPOSED"
    assert transition["adaptation"]["domain_state_hash"] == digest(state["domain"])
    assert transition["adaptation"]["sme_profile_hash"] == digest(state["sme"])
    assert transition["adaptation"]["selection_receipt_hash"] == state["selection_receipt"]["integrity_sha256"]
    assert transition["new_state_hash"] == state["new_state_hash"]

def test_receipt_and_state_are_deterministically_serializable():
    first = demo_unknown_domain()
    second = demo_unknown_domain()
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
