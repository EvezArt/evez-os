import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "desas-socratious.evex.json"

def canonical(document):
    copy = json.loads(json.dumps(document, ensure_ascii=False))
    copy.setdefault("integrity", {}).pop("sha256", None)
    return json.dumps(copy, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")

def main():
    doc = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    assert doc["evex"] == "EVEX"
    assert doc["version"] == 1
    assert doc["profile"] == "evez.exchange"
    assert doc["kind"] == "state.transition"
    transition = doc["transition"]
    assert transition["classification"]["state"] == "PROPOSED"
    assert transition["adaptation"]["profile"] == "desas-s.v1"
    assert transition["action"]["type"] == "desas.propose_question"
    assert transition["result"]["status"] == "SUCCEEDED"
    assert len(transition["adaptation"]["selection_receipt_hash"]) == 64
    assert transition["new_state_hash"] != transition["parent_state_hash"]
    assert hashlib.sha256(canonical(doc)).hexdigest() == doc["integrity"]["sha256"]
    print("PASS DESA-S EVEX interoperability fixture v1")

if __name__ == "__main__":
    main()
