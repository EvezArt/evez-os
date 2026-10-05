#!/usr/bin/env python3
import json,tempfile
from pathlib import Path
from unittest.mock import patch
from integrations.vcl_jev_evez import run

def vcl(s,manifest_id="default"): return {"id":"vcl-test","manifest_id":manifest_id,"status":"rendered","kind":"json_artifact","payload":s}
def jev(*a,**k): return {"ok":True,"source":"offline-fixture","model":"fixture","choice":"keep_unknown","raw_choice":"keep_unknown","confidence":0.96,"probabilities":{"keep_unknown":0.94,"promote_verified":0.06},"abstained":False}
def spine(d): return {"seq":17,"domain":"evidence","action":"VCL_JEV_REVIEW","data":d,"hash":"a"*64,"prev_hash":"b"*64}

with tempfile.TemporaryDirectory() as td:
    out=Path(td)/"bridge.json"
    with patch("integrations.vcl_jev_evez.render_vcl",vcl),patch("integrations.vcl_jev_evez.judge_jev",jev),patch("integrations.vcl_jev_evez.append_spine",spine):
        r=run({"claim":"phi=0.973","status":"UNKNOWN"},"Promote to VERIFIED?",{"keep_unknown":"insufficient","promote_verified":"sufficient"},out)
    assert r["jev"]["source"]=="offline-fixture" and r["jev"]["choice"]=="keep_unknown"
    assert r["spine"]["action"]=="VCL_JEV_REVIEW" and r["capsule"]["artifact_count"]==3
    from evidence.evidence_capsule import verify
    c=json.loads(json.dumps(r["capsule"])); c["artifacts"][0]["content"]='{"tampered":true}\n'
    assert not verify(c)["verified"]
print("VCL/JEV/EVEZ-OS bridge contract: PASS")
