import copy
from evez_file import seal,verify,loads,dumps
def sample():
 return {"evez":"EVEZ","version":1,"kind":"test","id":"test-001","created_at":"2026-10-05T00:00:00Z","state":"UNKNOWN","payload":{"value":42},"integrity":{"algorithm":"sha256","sha256":None}}
def test_seal_verify_roundtrip():
 d=seal(sample()); assert verify(d); assert loads(dumps(d),verify_integrity=True)==d
def test_tamper_fails():
 d=seal(sample()); x=copy.deepcopy(d); x["payload"]["value"]=43; assert not verify(x)
def test_unknown_fields_survive():
 d=seal(sample()); d["future_extension"]={"x":1}; assert loads(dumps(d))["future_extension"]=={"x":1}
