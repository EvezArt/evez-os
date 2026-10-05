#!/usr/bin/env python3
"""Civic Fusion: combine independently sourced accountability records.

The fusion engine never mutates source records. It creates a derived graph and
investigation queue whose every edge points back to source-record hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def normalize_name(value: str) -> str:
    value = value.upper().strip()
    value = re.sub(r"[^A-Z0-9 ]+", " ", value)
    value = re.sub(
        r"\b(INCORPORATED|INC|CORPORATION|CORP|COMPANY|CO|LIMITED|LTD|LLC|LP|PLC)\b",
        " ",
        value,
    )
    return re.sub(r"\s+", " ", value).strip()


def parse_date(value: str) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(value[:19], fmt)
        except ValueError:
            pass
    return None


def load(path: str) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected JSON object")
    return value


def entity_key(name: str) -> str:
    return normalize_name(name)


def records_from_report(report: dict, report_name: str) -> list[dict]:
    rows = report.get("records", [])
    if not isinstance(rows, list):
        raise SystemExit(f"{report_name}: records must be a list")
    result = []

    for row in rows:
        source_hash = row.get("record_sha256")
        if not source_hash:
            raise SystemExit(f"{report_name}: record missing record_sha256")

        entity = row.get("entity", "UNKNOWN")
        agency = row.get("agency", "UNKNOWN")
        date = row.get("date", "")
        amount = row.get("amount", 0)

        result.append({
            "report": report_name,
            "source_record_sha256": source_hash,
            "kind": row.get("kind", "unknown"),
            "entity": entity,
            "entity_key": entity_key(entity),
            "agency": agency,
            "agency_key": entity_key(agency),
            "date": date,
            "amount": amount,
            "award_id": row.get("award_id", ""),
            "source": row.get("source", {}),
        })

    return result


def cooccurrence(records: list[dict]) -> list[dict]:
    events = defaultdict(list)

    for row in records:
        date = parse_date(str(row["date"]))
        if date:
            events[date.date().isoformat()].append(row)

    signals = []
    for event_date, rows in sorted(events.items()):
        entities = sorted({r["entity_key"] for r in rows})
        if len(entities) < 2:
            continue

        for idx, left in enumerate(entities):
            for right in entities[idx + 1:]:
                left_rows = [r for r in rows if r["entity_key"] == left]
                right_rows = [r for r in rows if r["entity_key"] == right]

                if not left_rows or not right_rows:
                    continue

                signals.append({
                    "type": "same_day_entity_cooccurrence",
                    "severity": "REVIEW",
                    "date": event_date,
                    "entity_a": left,
                    "entity_b": right,
                    "records": [
                        r["source_record_sha256"]
                        for r in left_rows + right_rows
                    ],
                    "interpretation": "Temporal co-occurrence is a review lead, not evidence of a relationship.",
                })

    return signals


def cross_source_entity_overlap(records: list[dict]) -> list[dict]:
    by_entity = defaultdict(list)

    for row in records:
        by_entity[row["entity_key"]].append(row)

    signals = []
    for entity, rows in by_entity.items():
        sources = sorted({
            str(r.get("source", {}).get("name", "UNKNOWN"))
            for r in rows
        })

        if len(sources) < 2:
            continue

        signals.append({
            "type": "cross_source_entity_overlap",
            "severity": "HIGH_VALUE_REVIEW",
            "entity": entity,
            "source_count": len(sources),
            "sources": sources,
            "records": [r["source_record_sha256"] for r in rows],
            "interpretation": "Same normalized name across independent sources is a candidate linkage; identity must be verified using stronger identifiers.",
        })

    return signals


def graph(records: list[dict]) -> dict:
    nodes: dict[str, dict] = {}
    edges = []

    for row in records:
        entity_id = "entity:" + row["entity_key"]
        agency_id = "agency:" + row["agency_key"]

        nodes.setdefault(
            entity_id,
            {
                "id": entity_id,
                "type": "entity",
                "label": row["entity"],
            },
        )
        nodes.setdefault(
            agency_id,
            {
                "id": agency_id,
                "type": "agency",
                "label": row["agency"],
            },
        )

        edges.append({
            "source": agency_id,
            "target": entity_id,
            "relationship": row["kind"],
            "amount": row["amount"],
            "date": row["date"],
            "award_id": row["award_id"],
            "source_record_sha256": row["source_record_sha256"],
        })

    return {"nodes": list(nodes.values()), "edges": edges}


def fuse(paths: list[tuple[str, str]]) -> dict:
    records: list[dict] = []
    reports = []

    for name, path in paths:
        report = load(path)
        reports.append({
            "name": name,
            "result_sha256": report.get("result_sha256"),
            "record_count": report.get("record_count", 0),
            "source": report.get("generated_from", {}),
        })
        records.extend(records_from_report(report, name))

    signals = []
    signals.extend(cross_source_entity_overlap(records))
    signals.extend(cooccurrence(records))

    result = {
        "schema_version": 1,
        "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "reports": reports,
        "record_count": len(records),
        "records": records,
        "graph": graph(records),
        "investigation_queue": signals,
        "epistemic_rule": "CROSS_SOURCE_OVERLAP != IDENTITY_PROOF != WRONGDOING",
        "result_sha256": None,
    }

    result["result_sha256"] = sha(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "reports",
        nargs="+",
        help="name=path pairs produced by the Arsenal Ledger",
    )
    parser.add_argument("--output")

    args = parser.parse_args()

    pairs = []
    for item in args.reports:
        if "=" not in item:
            raise SystemExit("reports must use name=path form")
        name, path = item.split("=", 1)
        pairs.append((name, path))

    result = fuse(pairs)
    text = json.dumps(result, indent=2, sort_keys=True)

    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
