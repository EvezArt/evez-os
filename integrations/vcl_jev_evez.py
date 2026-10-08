#!/usr/bin/env python3
"""Bridge VCL render -> typed JEV judgement -> EVEZ-OS spine + capsule."""
from __future__ import annotations
import argparse,hashlib,json,os,urllib.error,urllib.request
from datetime import datetime,timezone
from pathlib import Path
from typing import Any

VCL_URL=os.environ.get("EVEZ_VCL_URL","https://evez-vcl.onrender.com").rstrip("/")
JEV_URL=os.environ.get("JEV_ENDPOINT","https://api.typesafe.ai/v1/systemone")
SPINE_URL=os.environ.get("EVEZ_SPINE_URL","http://127.0.0.1:9116").rstrip("/")
MODEL=os.environ.get("JEV_MODEL","jev-latest")
MIN_CONF=float(os.environ.get("JEV_MIN_CONFIDENCE","0.55"))

class BridgeUnavailable(RuntimeError): pass
def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def canon(x:Any)->bytes: return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
def digest(b:bytes)->str: return hashlib.sha256(b).hexdigest()

def request_json(url,method="GET",body=None,headers=None,timeout=30):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(url,data=data,method=method,headers={"Accept":"application/json","Content-Type":"application/json",**(headers or {})})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise BridgeUnavailable(f"HTTP {e.code} from {url}: {e.read().decode('utf-8','replace')[:300]}") from e
    except Exception as e: raise BridgeUnavailable(f"{type(e).__name__} from {url}: {str(e)[:200]}") from e

def render_vcl(state,manifest_id="default"):
    return request_json(f"{VCL_URL}/render","POST",{"manifest_id":manifest_id,"data":state})

def judge_jev(state,question,criteria):
    key=os.environ.get("TYPESAFE_API_KEY","").strip()
    if not key:
        return {"ok":False,"source":"unavailable","reason":"TYPESAFE_API_KEY is not set","question":question,"choice":None,"confidence":None,"probabilities":{}}
    p=request_json(JEV_URL,"POST",{"state":state,"model":MODEL,"questions":{"disposition":{"type":"choice","instructions":question,"criteria":criteria}}},{"Authorization":f"Bearer {key}"})
    raw=(p.get("answers") or {}).get("disposition")
    if not raw: raise BridgeUnavailable("JEV response missing answers.disposition")
    conf=raw.get("confidence")
    probs={k:float(v) for k,v in (raw.get("probabilities") or {}).items()}
    abstain=conf is None or float(conf)<MIN_CONF
    return {"ok":True,"source":"jev","model":p.get("model",MODEL),"question":question,"choice":None if abstain else raw.get("choice"),"raw_choice":raw.get("choice"),"confidence":conf,"probabilities":probs,"abstained":abstain,"min_confidence":MIN_CONF}

def append_spine(data):
    return request_json(f"{SPINE_URL}/append","POST",{"domain":"evidence","action":"VCL_JEV_REVIEW","data":data})

def capsule(vcl,jev,spine):
    rows=[]
    for name,obj in [("vcl-artifact.json",vcl),("jev-decision.json",jev),("spine-event.json",spine)]:
        raw=(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
        rows.append({"name":name,"media_type":"application/json","encoding":"utf-8","size":len(raw),"sha256":digest(raw),"content":raw.decode()})
    c={"schema_version":1,"capsule_type":"EVEZ_EVIDENCE_CAPSULE","created_at":now(),"metadata":{"bridge":"vcl-jev-evez-os","live_jev":jev.get("source")=="jev","epistemic_status":"integrity_only"},"artifact_count":3,"manifest":[{k:r[k] for k in ("name","media_type","encoding","size","sha256")} for r in rows],"artifacts":rows,"epistemic_rule":"CAPSULE_INTEGRITY != CLAIM_TRUTH != EXPLANATION","capsule_sha256":None}
    c["capsule_sha256"]=digest(canon(c)); return c

def run(state,question,criteria,output=None):
    vcl=render_vcl(state)
    jev=judge_jev({"vcl_artifact":vcl,"state":state},question,criteria)
    spine=append_spine({"timestamp":now(),"vcl_artifact_id":vcl.get("id"),"jev_source":jev.get("source"),"jev_model":jev.get("model"),"jev_choice":jev.get("choice"),"jev_raw_choice":jev.get("raw_choice"),"jev_confidence":jev.get("confidence"),"jev_probabilities":jev.get("probabilities"),"abstained":jev.get("abstained",True)})
    result={"bridge":"vcl-jev-evez-os","timestamp":now(),"vcl":vcl,"jev":jev,"spine":spine,"capsule":capsule(vcl,jev,spine)}
    if output: Path(output).parent.mkdir(parents=True,exist_ok=True); Path(output).write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--state",required=True); ap.add_argument("--question",required=True); ap.add_argument("--criteria",required=True); ap.add_argument("--output",default="artifacts/vcl-jev-evez-os.json"); a=ap.parse_args()
    r=run(json.loads(Path(a.state).read_text()),a.question,json.loads(a.criteria),a.output)
    print(json.dumps({"ok":True,"vcl_artifact_id":r["vcl"].get("id"),"jev_source":r["jev"].get("source"),"jev_choice":r["jev"].get("choice"),"jev_confidence":r["jev"].get("confidence"),"spine_seq":r["spine"].get("seq"),"capsule_sha256":r["capsule"]["capsule_sha256"],"output":a.output},sort_keys=True))
