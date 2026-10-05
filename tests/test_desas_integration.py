import hashlib
import json
from pathlib import Path

from evez_file import load, verify

ROOT = Path(__file__).resolve().parents[1]
EVEZ_EXAMPLE = ROOT / "examples" / "desas-socratious.evez"
EVEX_EXAMPLE = ROOT / "examples" / "desas-socratious.evex.json"

def test_desas_evez_example_is_sealed_and_valid():
    document = load(EVEZ_EXAMPLE, verify_integrity=True)
    assert verify(document)
    assert document["kind"] == "desas.adaptive.state"
    assert document["state"] == "PROPOSED"
    assert document["payload"]["profile"] == "desas-s.v1"

def test_desas_evex_example_is_sealed_and_bound():
    document = json.loads(EVEX_EXAMPLE.read_text(encoding="utf-8"))
    check = json.loads(json.dumps(document, ensure_ascii=False))
    check["integrity"].pop("sha256", None)
    canonical = json.dumps(check, ensure_ascii=False, sort_keys=True,
                            separators=(",", ":"), allow_nan=False).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == document["integrity"]["sha256"]
    assert document["transition"]["adaptation"]["profile"] == "desas-s.v1"
    assert document["transition"]["classification"]["state"] == "PROPOSED"
