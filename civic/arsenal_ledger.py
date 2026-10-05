#!/usr/bin/env python3
"""Arsenal Ledger: public-data accountability engine.

Purpose:
- normalize public procurement / influence records
- compute transparent concentration and linkage signals
- preserve source provenance
- generate investigation leads without asserting wrongdoing

This is a research/accountability tool, not an accusation engine.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "civic" / "arsenal-schema.json"


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def load_rows(path: str) -> list[dict]:
    file = Path(path)
    if file.suffix.lower() == ".json":
        value = json.loads(file.read_text(encoding="utf-8"))
        if isinstance(value, list):
            return value
        if isinstance(value, dict) and isinstance(value.get("records"), list):
            return value["records"]
        raise SystemExit("JSON input must be a list or an object containing records")

    with file.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize(rows: list[dict], source_name: str, source_uri: str) -> list[dict]:
    normalized = []
    for row in rows:
        kind = str(row.get("kind") or row.get("record_type") or "unknown").lower()
        entity = str(
            row.get("recipient")
            or row.get("recipient_name")
            or row.get("company")
            or row.get("registrant")
            or "UNKNOWN"
        ).strip()

        agency = str(
            row.get("agency")
            or row.get("awarding_agency")
            or row.get("client")
            or "UNKNOWN"
        ).strip()

        amount_raw = row.get("amount") or row.get("obligation") or row.get("award_amount") or 0
        try:
            amount = float(str(amount_raw).replace(",", "").replace("$", ""))
        except ValueError:
            amount = 0.0

        event_date = str(
            row.get("date")
            or row.get("award_date")
            or row.get("transaction_date")
            or ""
        ).strip()

        record = {
            "kind": kind,
            "entity": entity,
            "agency": agency,
            "amount": amount,
            "date": event_date,
            "award_id": str(row.get("award_id") or row.get("contract_id") or ""),
            "source": {
                "name": source_name,
                "uri": source_uri,
                "row_sha256": digest(row),
            },
        }
        record["record_sha256"] = digest(record)
        normalized.append(record)

    return normalized


def concentration(records: list[dict]) -> list[dict]:
    by_agency: dict[str, list[dict]] = defaultdict(list)
    for row in records:
        if row["amount"] > 0:
            by_agency[row["agency"]].append(row)

    signals = []
    for agency, rows in by_agency.items():
        total = sum(r["amount"] for r in rows)
        by_entity: dict[str, float] = defaultdict(float)
        for row in rows:
            by_entity[row["entity"]] += row["amount"]

        ranked = sorted(by_entity.items(), key=lambda item: item[1], reverse=True)
        if not ranked or total <= 0:
            continue

        top_entity, top_amount = ranked[0]
        share = top_amount / total

        if share >= 0.50:
            severity = "HIGH_SIGNAL"
        elif share >= 0.30:
            severity = "MEDIUM_SIGNAL"
        else:
            severity = "LOW_SIGNAL"

        signals.append({
            "type": "recipient_concentration",
            "severity": severity,
            "agency": agency,
            "top_entity": top_entity,
            "top_amount": round(top_amount, 2),
            "agency_total": round(total, 2),
            "top_share": round(share, 6),
            "interpretation": "Concentration is an investigation signal, not evidence of wrongdoing.",
        })

    return signals


def sole_source_signal(records: list[dict]) -> list[dict]:
    by_award = defaultdict(list)
    for row in records:
        award_id = row.get("award_id")
        if award_id:
            by_award[award_id].append(row)

    signals = []
    for award_id, rows in by_award.items():
        flags = {str(r.get("sole_source") or r.get("is_sole_source") or "").lower() for r in rows}
        if "true" not in flags and "yes" not in flags:
            continue

        amount = max((r["amount"] for r in rows), default=0.0)
        signals.append({
            "type": "sole_source",
            "severity": "REVIEW",
            "award_id": award_id,
            "amount": round(amount, 2),
            "interpretation": "Sole-source status is a procurement condition requiring context, not proof of misconduct.",
        })

    return signals


def repeated_counterparty(records: list[dict]) -> list[dict]:
    pairs: dict[tuple[str, str], int] = defaultdict(int)
    for row in records:
        pairs[(row["agency"], row["entity"])] += 1

    signals = []
    for (agency, entity), count in pairs.items():
        if count >= 10:
            signals.append({
                "type": "repeated_counterparty",
                "severity": "REVIEW",
                "agency": agency,
                "entity": entity,
                "record_count": count,
                "interpretation": "Repeated awards may reflect legitimate specialization; inspect competition and contract structure.",
            })
    return signals


def graph(records: list[dict], signals: list[dict]) -> dict:
    nodes = {}
    edges = []

    for row in records:
        entity_key = "entity:" + row["entity"].lower()
        agency_key = "agency:" + row["agency"].lower()
        nodes[entity_key] = {"id": entity_key, "type": "entity", "label": row["entity"]}
        nodes[agency_key] = {"id": agency_key, "type": "agency", "label": row["agency"]}
        edges.append({
            "source": agency_key,
            "target": entity_key,
            "type": row["kind"],
            "amount": row["amount"],
            "award_id": row["award_id"],
            "record_sha256": row["record_sha256"],
        })

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "signals": signals,
    }


def run(input_path: str, source_name: str, source_uri: str) -> dict:
    raw = load_rows(input_path)
    records = normalize(raw, source_name, source_uri)

    signals = []
    signals.extend(concentration(records))
    signals.extend(sole_source_signal(records))
    signals.extend(repeated_counterparty(records))

    result = {
        "schema_version": 1,
        "generated_from": {
            "source_name": source_name,
            "source_uri": source_uri,
            "input_sha256": hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),
        },
        "record_count": len(records),
        "records": records,
        "signals": signals,
        "graph": graph(records, signals),
        "epistemic_rule": "SIGNAL != ALLEGATION != PROOF",
        "result_sha256": None,
    }
    unsigned = dict(result)
    result["result_sha256"] = digest(unsigned)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--source-uri", required=True)
    parser.add_argument("--output")

    args = parser.parse_args()
    result = run(args.input, args.source_name, args.source_uri)
    text = json.dumps(result, indent=2, sort_keys=True)

    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
