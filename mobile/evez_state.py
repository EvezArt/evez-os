#!/usr/bin/env python3
"""Local evidence and offline outbox state for the EVEZ mobile operator.

The file format is intentionally boring: newline-delimited JSON, canonicalized
before hashing, with a parent hash connecting each record to the previous one.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def state_dir() -> Path:
    value = os.environ.get("EVEZ_STATE_DIR")
    path = Path(value) if value else Path.home() / ".local" / "state" / "evez"
    path.mkdir(parents=True, exist_ok=True)
    return path


def append_line(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for number, raw in enumerate(handle, 1):
            raw = raw.rstrip("\n")
            if not raw:
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{number}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise SystemExit(f"{path}:{number}: expected JSON object")
            rows.append(value)
    return rows


def record(event_type: str, payload: object, queue: bool) -> dict:
    spine = state_dir() / "spine.jsonl"
    rows = read_jsonl(spine)
    previous = rows[-1].get("hash", "GENESIS") if rows else "GENESIS"
    event_id = str(uuid.uuid4())

    core = {
        "event_id": event_id,
        "timestamp": now(),
        "type": event_type,
        "parent_hash": previous,
        "payload": payload,
    }
    digest = hashlib.sha256(canonical(core)).hexdigest()
    row = {**core, "hash": digest}
    append_line(spine, row)

    if queue:
        append_line(
            state_dir() / "outbox.jsonl",
            {
                "event_id": event_id,
                "queued_at": row["timestamp"],
                "type": event_type,
                "payload": payload,
            },
        )

    return {
        "recorded": True,
        "queued": queue,
        "event_id": event_id,
        "hash": digest,
        "parent_hash": previous,
        "spine": str(spine),
    }


def verify() -> dict:
    spine = state_dir() / "spine.jsonl"
    rows = read_jsonl(spine)
    previous = "GENESIS"

    for number, row in enumerate(rows, 1):
        required = {"event_id", "timestamp", "type", "parent_hash", "payload", "hash"}
        missing = sorted(required.difference(row))
        if missing:
            return {"verified": False, "line": number, "error": "missing fields", "missing": missing}

        if row["parent_hash"] != previous:
            return {
                "verified": False,
                "line": number,
                "error": "parent hash mismatch",
                "expected_parent": previous,
                "actual_parent": row["parent_hash"],
            }

        core = {key: row[key] for key in ("event_id", "timestamp", "type", "parent_hash", "payload")}
        expected = hashlib.sha256(canonical(core)).hexdigest()
        if row["hash"] != expected:
            return {
                "verified": False,
                "line": number,
                "error": "record hash mismatch",
                "expected_hash": expected,
                "actual_hash": row["hash"],
            }

        previous = row["hash"]

    return {
        "verified": True,
        "records": len(rows),
        "head": previous,
        "spine": str(spine),
    }


def outbox() -> dict:
    rows = read_jsonl(state_dir() / "outbox.jsonl")
    return {"queued": len(rows), "events": rows}


def atomic_replace_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass


def sync(endpoint: str, path: str, limit: int) -> dict:
    outbox_path = state_dir() / "outbox.jsonl"
    rows = read_jsonl(outbox_path)
    receipts_path = state_dir() / "sync_receipts.jsonl"
    processed = 0
    failed = 0

    if endpoint.endswith("/"):
        endpoint = endpoint[:-1]
    url = endpoint + (path if path.startswith("/") else "/" + path)

    for item in rows[:limit]:
        body = canonical({"type": item["type"], "payload": item["payload"]})
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Idempotency-Key": item["event_id"],
        }
        token = os.environ.get("EVEZ_AUTH_TOKEN")
        if token:
            headers["Authorization"] = "Bearer " + token

        req = request.Request(url, data=body, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=30) as response:
                response_body = response.read()
                status = int(response.status)
            receipt = {
                "timestamp": now(),
                "event_id": item["event_id"],
                "status": status,
                "response_sha256": hashlib.sha256(response_body).hexdigest(),
                "delivered": 200 <= status < 300,
            }
            append_line(receipts_path, receipt)

            if not receipt["delivered"]:
                failed += 1
                break
            rows.pop(0)
            processed += 1

        except error.HTTPError as exc:
            failed += 1
            append_line(
                receipts_path,
                {
                    "timestamp": now(),
                    "event_id": item["event_id"],
                    "status": int(exc.code),
                    "delivered": False,
                    "error": "HTTPError",
                },
            )
            break
        except error.URLError as exc:
            failed += 1
            append_line(
                receipts_path,
                {
                    "timestamp": now(),
                    "event_id": item["event_id"],
                    "delivered": False,
                    "error": "URLError",
                    "reason": str(exc.reason),
                },
            )
            break

    atomic_replace_jsonl(outbox_path, rows)
    return {
        "synced": processed,
        "failed": failed,
        "remaining": len(rows),
        "endpoint": url,
        "receipts": str(receipts_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_record = sub.add_parser("record")
    p_record.add_argument("type")
    p_record.add_argument("payload")
    p_record.add_argument("--queue", action="store_true")

    sub.add_parser("verify")
    sub.add_parser("outbox")

    p_sync = sub.add_parser("sync")
    p_sync.add_argument("endpoint")
    p_sync.add_argument("path")
    p_sync.add_argument("--limit", type=int, default=25)

    args = parser.parse_args()

    if args.command == "record":
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError as exc:
            print(json.dumps({"recorded": False, "error": str(exc)}))
            return 2
        print(json.dumps(record(args.type, payload, args.queue), sort_keys=True))
        return 0

    if args.command == "verify":
        result = verify()
        print(json.dumps(result, sort_keys=True))
        return 0 if result["verified"] else 1

    if args.command == "outbox":
        print(json.dumps(outbox(), sort_keys=True))
        return 0

    if args.command == "sync":
        result = sync(args.endpoint, args.path, max(1, args.limit))
        print(json.dumps(result, sort_keys=True))
        return 1 if result["failed"] else 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
