import copy
from evez_file import EVEZFormatError, seal, verify, dumps, loads

def sample():
    return {
        "evez": "EVEZ",
        "version": 1,
        "kind": "test",
        "id": "test-001",
        "created_at": "2026-10-05T00:00:00Z",
        "state": "UNKNOWN",
        "payload": {"value": 42},
        "integrity": {"algorithm": "sha256", "sha256": None},
    }

def test_seal_and_verify():
    doc = seal(sample())
    assert verify(doc)
    assert loads(dumps(doc), verify_integrity=True) == doc

def test_payload_tamper_fails():
    doc = seal(sample())
    tampered = copy.deepcopy(doc)
    tampered["payload"]["value"] = 43
    assert not verify(tampered)

def test_marker_required():
    doc = sample()
    doc["evez"] = "NOT-EVEZ"
    try:
        seal(doc)
    except EVEZFormatError:
        pass
    else:
        raise AssertionError("invalid marker accepted")
