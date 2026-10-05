"""Portable EVEZ v1 reader/writer/verifier."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any
EVEZ_EXTENSION=".evez"
EVEZ_MEDIA_TYPE="application/vnd.evez+json"
EVEZ_MAGIC="EVEZ"
EVEZ_VERSION=1
STATES={"VERIFIED","SUPPORTED","INFERRED","PROPOSED","UNKNOWN","STALE","CONTRADICTED","RETRACTED"}
class EVEZFormatError(ValueError): pass
def canonical_bytes(document:dict[str,Any])->bytes:
    copy=json.loads(json.dumps(document,ensure_ascii=False))
    copy.setdefault("integrity",{}).pop("sha256",None)
    return json.dumps(copy,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")
def digest(document:dict[str,Any])->str: return hashlib.sha256(canonical_bytes(document)).hexdigest()
def validate(document:dict[str,Any])->None:
    required={"evez","version","kind","id","created_at","state","payload","integrity"}
    missing=required-document.keys()
    if missing: raise EVEZFormatError(f"missing required fields: {sorted(missing)}")
    if document["evez"]!=EVEZ_MAGIC or document["version"]!=EVEZ_VERSION: raise EVEZFormatError("unsupported EVEZ document")
    if not isinstance(document["kind"],str) or not document["kind"]: raise EVEZFormatError("kind must be non-empty")
    if not isinstance(document["id"],str) or not document["id"]: raise EVEZFormatError("id must be non-empty")
    if document["state"] not in STATES: raise EVEZFormatError("invalid epistemic state")
    if not isinstance(document["payload"],dict): raise EVEZFormatError("payload must be an object")
    if not isinstance(document["integrity"],dict) or document["integrity"].get("algorithm")!="sha256": raise EVEZFormatError("sha256 integrity required")
def seal(document:dict[str,Any])->dict[str,Any]:
    validate(document); out=json.loads(json.dumps(document,ensure_ascii=False)); out["integrity"]={"algorithm":"sha256","sha256":None}; out["integrity"]["sha256"]=digest(out); return out
def verify(document:dict[str,Any])->bool:
    validate(document); return document["integrity"].get("sha256") is not None and document["integrity"]["sha256"]==digest(document)
def loads(text:str,verify_integrity=False)->dict[str,Any]:
    try: obj=json.loads(text)
    except json.JSONDecodeError as exc: raise EVEZFormatError(str(exc)) from exc
    if not isinstance(obj,dict): raise EVEZFormatError("root must be object")
    validate(obj)
    if verify_integrity and not verify(obj): raise EVEZFormatError("integrity verification failed")
    return obj
def dumps(document:dict[str,Any],seal_document=True)->str:
    obj=seal(document) if seal_document else document; validate(obj); return json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
def load(path:str|Path,verify_integrity=False): return loads(Path(path).read_text(encoding="utf-8"),verify_integrity)
def dump(document,path): Path(path).write_text(dumps(document),encoding="utf-8")
