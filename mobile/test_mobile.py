#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "evez_state.py"
CTL = ROOT / "evezctl"


def run_state(temp: str, *args, expect: int = 0) -> dict:
    env = os.environ.copy()
    env["EVEZ_STATE_DIR"] = temp
    result = subprocess.run(
        [sys.executable, str(STATE), *args],
        env=env,
        text=True,
        capture_output=True,
    )
    if result.returncode != expect:
        raise AssertionError((args, result.returncode, result.stdout, result.stderr))
    return json.loads(result.stdout)


def run_ctl(temp_root: Path, *args: str, expect: int = 0) -> dict:
    env = os.environ.copy()
    state_dir = temp_root / "state"
    log_dir = temp_root / "logs"
    env.update(
        {
            "HOME": str(temp_root),
            "EVEZ_CONFIG": str(temp_root / "missing.env"),
            "EVEZ_ROOT": str(ROOT.parent),
            "EVEZ_STATE_DIR": str(state_dir),
            "EVEZ_LOG_DIR": str(log_dir),
        }
    )
    result = subprocess.run(
        ["bash", str(CTL), *args],
        env=env,
        text=True,
        capture_output=True,
    )
    if result.returncode != expect:
        raise AssertionError((args, result.returncode, result.stdout, result.stderr))

    for line in reversed(result.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    raise AssertionError((args, "missing JSON output", result.stdout, result.stderr))


class SyncHandler(BaseHTTPRequestHandler):
    statuses = [503, 204, 204]
    requests: list[tuple[int, str | None]] = []
    lock = threading.Lock()

    def do_POST(self) -> None:
        request_number = len(self.requests)
        status = self.statuses[min(request_number, len(self.statuses) - 1)]
        key = self.headers.get("Idempotency-Key")
        with self.lock:
            self.requests.append((status, key))

        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)

        self.send_response(status)
        self.end_headers()
        if status != 204:
            self.wfile.write(b"temporary failure")

    def log_message(self, format: str, *args: object) -> None:
        return


with tempfile.TemporaryDirectory() as temp:
    one = run_state(temp, "record", "BOOT", '{"mode":"offline"}', "--queue")
    assert one["recorded"] and one["queued"]

    two = run_state(temp, "record", "OBSERVATION", '{"value":42}', "--queue")
    assert two["parent_hash"] == one["hash"]

    checked = run_state(temp, "verify")
    assert checked["verified"] and checked["records"] == 2

    queued = run_state(temp, "outbox")
    assert queued["queued"] == 2

    server = ThreadingHTTPServer(("127.0.0.1", 0), SyncHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        endpoint = f"http://127.0.0.1:{server.server_port}"

        failed = run_ctl(
            Path(temp),
            "sync",
            "http://127.0.0.1:%s" % server.server_port,
            "/spine/event",
            expect=1,
        )
        assert failed["synced"] == 0
        assert failed["failed"] == 1
        assert failed["remaining"] == 2

        after_failure = run_ctl(Path(temp), "outbox")
        assert after_failure["queued"] == 2
        assert len(SyncHandler.requests) == 1
        assert SyncHandler.requests[0][0] == 503
        first_key = SyncHandler.requests[0][1]
        assert first_key

        original_endpoint = endpoint
        assert failed["endpoint"] == original_endpoint + "/spine/event"

        delivered = run_ctl(
            Path(temp),
            "sync",
            endpoint,
            "/spine/event",
            expect=0,
        )
        assert delivered["synced"] == 2
        assert delivered["failed"] == 0
        assert delivered["remaining"] == 0

        assert len(SyncHandler.requests) == 3
        statuses = [status for status, _ in SyncHandler.requests]
        keys = [key for _, key in SyncHandler.requests]
        assert statuses == [503, 204, 204]
        assert keys[0] == keys[1]
        assert keys[0] != keys[2]

        drained = run_ctl(Path(temp), "outbox")
        assert drained["queued"] == 0

        receipts = Path(temp) / "state" / "sync_receipts.jsonl"
        receipt_rows = [json.loads(line) for line in receipts.read_text(encoding="utf-8").splitlines()]
        assert [row["status"] for row in receipt_rows] == [503, 204, 204]
        assert receipt_rows[0]["delivered"] is False
        assert receipt_rows[1]["delivered"] is True
        assert receipt_rows[2]["delivered"] is True

        verified = run_ctl(Path(temp), "verify")
        assert verified["verified"] and verified["records"] == 2
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    spine = Path(temp) / "state" / "spine.jsonl"
    lines = spine.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["payload"]["mode"] = "tampered"
    spine.write_text(json.dumps(first) + "\n" + lines[1] + "\n", encoding="utf-8")

    broken = subprocess.run(
        [sys.executable, str(STATE), "verify"],
        env=os.environ | {"EVEZ_STATE_DIR": temp},
        text=True,
        capture_output=True,
    )
    assert broken.returncode != 0
    result = json.loads(broken.stdout)
    assert result["verified"] is False

print("mobile evidence tests: PASS")
