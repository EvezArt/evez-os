#!/usr/bin/env python3
"""Fail-closed Telegram command bridge for the EVEZ spacetime lab.

Not an arbitrary shell, LLM, or OpenClaw tool executor. Requires an explicit
numeric user allowlist, accepts private chats only, opens no inbound port, and
writes only a narrow set of auditable lab records.
"""
from __future__ import annotations
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from research import spacetime_breakthrough_lab as lab  # noqa: E402

MAX_MESSAGE_LENGTH = 4000
MAX_FIELD_LENGTH = 1000


def parse_allowed_user_ids(raw: str | None) -> set[int]:
    if not raw or not raw.strip():
        raise ValueError("TELEGRAM_ALLOWED_USER_IDS must list numeric user IDs")
    ids = set()
    for token in raw.split(","):
        token = token.strip()
        if not token.isdigit():
            raise ValueError("TELEGRAM_ALLOWED_USER_IDS contains a non-numeric ID")
        ids.add(int(token))
    if not ids:
        raise ValueError("TELEGRAM_ALLOWED_USER_IDS must not be empty")
    return ids


def split_fields(text: str, expected: int) -> list[str]:
    parts = [part.strip() for part in text.split("|")]
    if len(parts) != expected or any(not part for part in parts):
        raise ValueError(f"use exactly {expected} non-empty fields separated by |")
    if any(len(part) > MAX_FIELD_LENGTH for part in parts):
        raise ValueError("each field must be 1000 characters or fewer")
    return parts


def already_processed(update_id: int | None, ledger_path: Path) -> bool:
    if update_id is None or not ledger_path.exists():
        return False
    try:
        records = lab._load_ledger(ledger_path)
    except (OSError, lab.LabError):
        return False  # append_event itself refuses to extend a corrupt ledger
    return any(r.get("event", {}).get("transport_update_id") == update_id for r in records)


def handle_command(text: str, *, sender_id: int, chat_type: str, allowed_ids: set[int],
                   ledger_path: Path, update_id: int | None = None) -> str | None:
    if chat_type != "private" or sender_id not in allowed_ids:
        return None
    if not isinstance(text, str) or len(text) > MAX_MESSAGE_LENGTH:
        return "Message refused: command text exceeds the 4000-character limit."
    command, _, argument = text.strip().partition(" ")
    command = command.split("@", 1)[0].lower()
    argument = argument.strip()
    try:
        if command in {"/start", "/help"}:
            return (
                "EVEZ Spacetime Lab — restricted commands\n"
                "/status — ledger summary and integrity\n"
                "/verify — verify the local hash chain\n"
                "/proposal title | hypothesis | model — register a PROPOSED experiment\n"
                "/observation source | modality | quantity | value | unit | calibration_id | notes\n"
                "Modalities: simulation, lab_instrument, ruview_csi, published_literature, synthetic_test\n"
                "No shell, deploy, sensor control, arbitrary URL fetch, or agent execution is available."
            )
        if command in {"/status", "/verify"}:
            report = lab.experiment_summary(ledger_path)
            verification = report["verification"]
            if not verification["ok"]:
                return f"LEDGER INVALID: {verification.get('error', 'integrity check failed')}"
            experiment = report["experiment"]
            if experiment is None:
                return f"Ledger integrity OK; {verification['events']} events; no experiment registered."
            return (
                f"Ledger integrity OK · events={verification['events']} · observations={len(report['observations'])}\n"
                f"Experiment: {experiment['title']} ({experiment['experiment_id']})\n"
                f"Model: {experiment['model_name']} · class={experiment['claim_classification']} · status={experiment['epistemic_status']}\n"
                "Integrity is not evidence of physical truth or feasibility."
            )
        if already_processed(update_id, ledger_path):
            return "This Telegram update was already recorded; no duplicate action taken."
        if command == "/proposal":
            title, hypothesis, model_name = split_fields(argument, 3)
            experiment = lab.new_experiment(
                title=title, hypothesis=hypothesis, model_name=model_name,
                claim_classification="speculative",
                assumptions=["State the metric signature, coordinate conventions, boundary conditions, and approximations."],
                predictions=["Write at least one falsifiable, independently checkable prediction before testing."],
                controls=["Include a null/control case and document parameters and units."]
            )
            event = {"event_type": "SPACETIME_LAB.EXPERIMENT_REGISTERED", "experiment": experiment}
            if update_id is not None:
                event["transport_update_id"] = update_id
            result = lab.append_event(ledger_path, event)
            return f"Registered PROPOSED experiment {experiment['experiment_id']} (event {result['sequence']}). No feasibility claim made."
        if command == "/observation":
            source, modality, quantity, raw_value, unit, calibration_id, notes = split_fields(argument, 7)
            observation = {
                "source": source, "modality": modality, "quantity": quantity,
                "value": lab._json_value(raw_value), "unit": unit, "uncertainty": None,
                "calibration_id": calibration_id, "evidence_uri": None, "evidence_sha256": None,
                "notes": notes, "observed_at": lab.utc_now()
            }
            event = {"event_type": "SPACETIME_LAB.OBSERVATION_RECORDED", "observation": observation}
            if update_id is not None:
                event["transport_update_id"] = update_id
            result = lab.append_event(ledger_path, event)
            return f"Observation recorded as event {result['sequence']} ({result['event_hash'][:12]}…). Check source quality and calibration before interpretation."
        return "Unknown command. Use /help."
    except (ValueError, lab.LabError, OSError) as exc:
        return f"Command refused: {exc}"


def telegram_api(token: str, method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    # Do not print the URL or the underlying exception: the bot token is embedded in the URL.
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"} if data else {})
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            body = json.loads(response.read().decode("utf-8"))
        if not isinstance(body, dict) or not body.get("ok"):
            raise RuntimeError("Telegram Bot API returned a non-ok response")
        return body
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        raise RuntimeError("Telegram API request failed; details withheld to prevent token disclosure") from None


def main() -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print("TELEGRAM_BOT_TOKEN is required; do not put it in source control.", file=sys.stderr)
        return 2
    try:
        allowlist = parse_allowed_user_ids(os.environ.get("TELEGRAM_ALLOWED_USER_IDS"))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    ledger = Path(os.environ.get("EVEZ_SPACETIME_LEDGER", str(lab.DEFAULT_LEDGER))).expanduser()
    offset = 0
    print(f"EVEZ Spacetime Telegram bridge started; allowlisted users={len(allowlist)}; ledger={ledger}", flush=True)
    while True:
        try:
            updates = telegram_api(token, "getUpdates", {"offset": offset, "timeout": 25, "allowed_updates": ["message"]}).get("result", [])
            for update in updates:
                if not isinstance(update, dict) or not isinstance(update.get("update_id"), int):
                    continue
                offset = update["update_id"] + 1
                message = update.get("message") or {}
                sender = message.get("from") or {}
                chat = message.get("chat") or {}
                reply = handle_command(
                    message.get("text", ""), sender_id=sender.get("id", -1),
                    chat_type=chat.get("type", "unknown"), allowed_ids=allowlist,
                    ledger_path=ledger, update_id=update["update_id"]
                )
                if reply and isinstance(chat.get("id"), int):
                    telegram_api(token, "sendMessage", {"chat_id": chat["id"], "text": reply[:MAX_MESSAGE_LENGTH]})
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr, flush=True)
            time.sleep(3)
        except KeyboardInterrupt:
            print("EVEZ Spacetime Telegram bridge stopped.", flush=True)
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
