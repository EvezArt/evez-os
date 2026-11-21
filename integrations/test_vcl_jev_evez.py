#!/usr/bin/env python3
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from integrations.vcl_jev_evez import judge_jev, run


def vcl(state, manifest_id="default"):
    return {
        "id": "vcl-test",
        "manifest_id": manifest_id,
        "status": "rendered",
        "kind": "json_artifact",
        "payload": state,
    }


def jev(*args, **kwargs):
    return {
        "ok": True,
        "source": "offline-fixture",
        "model": "fixture",
        "choice": "keep_unknown",
        "raw_choice": "keep_unknown",
        "confidence": 0.96,
        "probabilities": {"keep_unknown": 0.94, "promote_verified": 0.06},
        "abstained": False,
    }


def spine(data):
    return {
        "seq": 17,
        "domain": "evidence",
        "action": "VCL_JEV_REVIEW",
        "data": data,
        "hash": "a" * 64,
        "prev_hash": "b" * 64,
    }


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "bridge.json"
    with patch("integrations.vcl_jev_evez.render_vcl", vcl),          patch("integrations.vcl_jev_evez.judge_jev", jev),          patch("integrations.vcl_jev_evez.append_spine", spine):
        result = run(
            {"claim": "phi=0.973", "status": "UNKNOWN"},
            "Promote to VERIFIED?",
            {"keep_unknown": "insufficient", "promote_verified": "sufficient"},
            out,
        )

    assert result["jev"]["source"] == "offline-fixture"
    assert result["jev"]["choice"] == "keep_unknown"
    assert result["spine"]["action"] == "VCL_JEV_REVIEW"
    assert result["capsule"]["artifact_count"] == 3

    from evidence.evidence_capsule import verify

    capsule_copy = json.loads(json.dumps(result["capsule"]))
    capsule_copy["artifacts"][0]["content"] = '{"tampered":true}\n'
    assert not verify(capsule_copy)["verified"]

# Contract test for the real JEV request shape, without contacting the service.
with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
    with patch("integrations.vcl_jev_evez.request_json", return_value={
        "model": "jev-latest",
        "answers": {
            "disposition": {
                "type": "choice",
                "choice": "keep_unknown",
                "probabilities": {"keep_unknown": 0.94, "promote_verified": 0.06},
                "confidence": 0.96,
            }
        },
    }) as request:
        answer = judge_jev(
            {"vcl_artifact": {"id": "vcl-test"}},
            "Promote to VERIFIED?",
            {"keep_unknown": "insufficient", "promote_verified": "sufficient"},
        )
        payload = request.call_args.args[2]
        assert payload["questions"]["disposition"]["type"] == "choice"
        assert payload["questions"]["disposition"]["instructions"] == "Promote to VERIFIED?"
        assert payload["questions"]["disposition"]["criteria"]["keep_unknown"] == "insufficient"
        assert answer["choice"] == "keep_unknown"
        assert answer["confidence"] == 0.96

# Auth header contract: if configured, VCL receives X-EVEZ-API-KEY.
with patch.dict(os.environ, {"EVEZ_VCL_API_KEY": "vcl-test-key"}):
    import integrations.vcl_jev_evez as bridge
    bridge.VCL_API_KEY = os.environ["EVEZ_VCL_API_KEY"]
    with patch("integrations.vcl_jev_evez.request_json", return_value={"id": "vcl-test"}) as request:
        bridge.render_vcl({"x": 1})
        assert request.call_args.args[3]["X-EVEZ-API-KEY"] == "vcl-test-key"

print("VCL/JEV/EVEZ-OS bridge contract: PASS")
