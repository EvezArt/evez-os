#!/usr/bin/env python3
from pathlib import Path
import json
import tempfile

from arsenal_ledger import run

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "records.json"
    path.write_text(Path("civic/sample-records.json").read_text(encoding="utf-8"), encoding="utf-8")

    result = run(
        str(path),
        "synthetic-test",
        "https://example.invalid/test"
    )

    assert result["record_count"] == 3
    signals = [s for s in result["signals"] if s["type"] == "recipient_concentration"]
    assert signals
    assert signals[0]["top_entity"] == "Example Defense Supplier A"
    assert signals[0]["severity"] == "HIGH_SIGNAL"
    assert result["epistemic_rule"] == "SIGNAL != ALLEGATION != PROOF"

print("arsenal ledger test: PASS")
