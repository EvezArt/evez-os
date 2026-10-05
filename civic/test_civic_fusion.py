#!/usr/bin/env python3
from pathlib import Path
import json
import tempfile

from civic_fusion import fuse


def report(name, record_hash, entity, source_name, date):
    record = {
        "kind": "campaign_finance",
        "entity": entity,
        "agency": "PUBLIC_ACTOR",
        "amount": 100,
        "date": date,
        "award_id": name,
        "source": {
            "name": source_name,
            "uri": "https://example.invalid/" + source_name,
        },
        "record_sha256": record_hash,
    }
    return {
        "record_count": 1,
        "records": [record],
        "result_sha256": "fixture-" + name,
        "generated_from": {"source_name": source_name},
    }


with tempfile.TemporaryDirectory() as tmp:
    a = Path(tmp) / "a.json"
    b = Path(tmp) / "b.json"

    a.write_text(json.dumps(report("a", "sha-a", "Example Supplier Inc.", "source-a", "2026-05-01")))
    b.write_text(json.dumps(report("b", "sha-b", "EXAMPLE SUPPLIER", "source-b", "2026-05-01")))

    result = fuse([("contracts", str(a)), ("finance", str(b))])

    overlap = [
        item
        for item in result["investigation_queue"]
        if item["type"] == "cross_source_entity_overlap"
    ]
    assert overlap
    assert overlap[0]["source_count"] == 2
    assert result["epistemic_rule"] == "CROSS_SOURCE_OVERLAP != IDENTITY_PROOF != WRONGDOING"

print("civic fusion test: PASS")
