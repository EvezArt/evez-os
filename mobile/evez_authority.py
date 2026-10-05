#!/usr/bin/env python3
"""Command authority and dual-control layer for EVEZ-OS.

This layer is defensive: it makes high-impact operations harder to authorize
accidentally or by replay. It does not claim classified or military approval.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import subprocess
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "security" / "mobile-policy.json"
DEFAULT_DIR = Path.home() / ".config" / "evez" / "authority"

def canon(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()

def now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)

def stamp(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")

def authority_dir() -> Path:
    value = os.environ.get("EVEZ_AUTHORITY_DIR")
    path = Path(value) if value else DEFAULT_DIR
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)
    return path

def epoch_path() -> Path:
    return authority_dir() / "epoch"

def current_epoch() -> int:
    path = epoch_path()
    if not path.exists():
        path.write_text("1\n", encoding="utf-8")
        os.chmod(path, 0o600)
    return int(path.read_text(encoding="utf-8").strip())

def advance_epoch() -> int:
    value = current_epoch() + 1
    epoch_path().write_text(f"{value}\n", encoding="utf-8")
    return value

def run(cmd: list[str], input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(cmd, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

def role_paths(role: str) -> tuple[Path, Path]:
    safe = role.lower().replace("/", "_")
    base = authority_dir()
    return base / f"{safe}-private.pem", base / f"{safe}-public.pem"

def init_role(role: str) -> dict:
    if role not in {"operator", "reviewer"}:
        raise SystemExit("role must be operator or reviewer")

    private, public = role_paths(role)
    if private.exists() or public.exists():
        return {"initialized": False, "role": role, "reason": "role key already exists", "public_key": str(public)}

    password = getpass.getpass(f"Create {role} key passphrase: ")
    confirm = getpass.getpass(f"Repeat {role} key passphrase: ")
    if not password or password != confirm:
        raise SystemExit("DENY: passphrases do not match or are empty")

    generated = run(
        ["openssl", "genpkey", "-algorithm", "ED25519", "-aes-256-cbc", "-pass", "stdin", "-out", str(private)],
        (password + "\n").encode(),
    )
    if generated.returncode != 0:
        raise SystemExit(generated.stderr.decode(errors="replace"))

    exported = run(
        ["openssl", "pkey", "-passin", "stdin", "-in", str(private), "-pubout", "-out", str(public)],
        (password + "\n").encode(),
    )
    if exported.returncode != 0:
        private.unlink(missing_ok=True)
        raise SystemExit(exported.stderr.decode(errors="replace"))

    os.chmod(private, 0o600)
    os.chmod(public, 0o644)

    public_bytes = public.read_bytes()
    fingerprint = hashlib.sha256(public_bytes).hexdigest()
    return {"initialized": True, "role": role, "public_key": str(public), "fingerprint": fingerprint}

def sign(role: str, action: str, payload: Any, ttl_minutes: int) -> dict:
    private, public = role_paths(role)
    if not private.exists() or not public.exists():
        raise SystemExit(f"DENY: initialize {role} key first")

    epoch = current_epoch()
    issued = now()
    expires = issued + timedelta(minutes=max(1, min(ttl_minutes, 30)))

    envelope = {
        "version": 1,
        "operation_id": str(uuid.uuid4()),
        "action": action,
        "role": role,
        "epoch": epoch,
        "issued_at": stamp(issued),
        "expires_at": stamp(expires),
        "payload": payload,
    }

    message = canon(envelope)
    message_hash = hashlib.sha256(message).hexdigest()
    password = getpass.getpass(f"{role} signing passphrase: ")

    with tempfile.TemporaryDirectory() as tmp:
        message_path = Path(tmp) / "message.bin"
        sig_path = Path(tmp) / "signature.bin"
        message_path.write_bytes(message)

        signed = run(
            ["openssl", "pkeyutl", "-sign", "-inkey", str(private),
             "-passin", "stdin", "-rawin", "-in", str(message_path), "-out", str(sig_path)],
            (password + "\n").encode(),
        )
        if signed.returncode != 0:
            raise SystemExit("DENY: signing failed")

        signature = sig_path.read_bytes().hex()

    result = {
        "envelope": envelope,
        "signature_hex": signature,
        "public_key": str(public),
        "public_key_sha256": hashlib.sha256(public.read_bytes()).hexdigest(),
        "message_sha256": message_hash,
    }

    operations = authority_dir() / "operations"
    operations.mkdir(parents=True, exist_ok=True)
    output = operations / f"{envelope['operation_id']}-{role}.json"
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    os.chmod(output, 0o600)
    result["saved_to"] = str(output)
    return result

def verify(path: str, trusted_public: str, required_role: str | None = None) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    envelope = value["envelope"]
    current = current_epoch()

    if envelope["epoch"] != current:
        return {"verified": False, "error": "stale security epoch", "expected": current, "actual": envelope["epoch"]}

    if required_role and envelope["role"] != required_role:
        return {"verified": False, "error": "wrong role", "expected": required_role, "actual": envelope["role"]}

    expires = datetime.fromisoformat(envelope["expires_at"].replace("Z", "+00:00"))
    if now() > expires:
        return {"verified": False, "error": "operation expired"}

    message = canon(envelope)
    expected = hashlib.sha256(message).hexdigest()
    if value["message_sha256"] != expected:
        return {"verified": False, "error": "message digest mismatch"}

    public_bytes = Path(trusted_public).read_bytes()
    if hashlib.sha256(public_bytes).hexdigest() != value["public_key_sha256"]:
        return {"verified": False, "error": "trusted public key fingerprint mismatch"}

    signature = bytes.fromhex(value["signature_hex"])
    with tempfile.TemporaryDirectory() as tmp:
        msg = Path(tmp) / "message.bin"
        sig = Path(tmp) / "signature.bin"
        msg.write_bytes(message)
        sig.write_bytes(signature)
        checked = run([
            "openssl", "pkeyutl", "-verify", "-pubin", "-inkey", trusted_public,
            "-rawin", "-in", str(msg), "-sigfile", str(sig)
        ])

    return {
        "verified": checked.returncode == 0,
        "operation_id": envelope["operation_id"],
        "role": envelope["role"],
        "epoch": envelope["epoch"],
        "message_sha256": expected,
    }

def quorum(path_a: str, path_b: str, key_a: str, key_b: str) -> dict:
    one = json.loads(Path(path_a).read_text(encoding="utf-8"))
    two = json.loads(Path(path_b).read_text(encoding="utf-8"))

    a = one["envelope"]
    b = two["envelope"]

    if a["operation_id"] != b["operation_id"]:
        return {"approved": False, "error": "operation IDs differ"}
    if a["action"] != b["action"]:
        return {"approved": False, "error": "actions differ"}
    if canon(a.get("payload")) != canon(b.get("payload")):
        return {"approved": False, "error": "payloads differ"}
    if a["epoch"] != b["epoch"] or a["epoch"] != current_epoch():
        return {"approved": False, "error": "security epoch mismatch"}
    if {a["role"], b["role"]} != {"operator", "reviewer"}:
        return {"approved": False, "error": "dual-control roles not satisfied"}
    if one["public_key_sha256"] == two["public_key_sha256"]:
        return {"approved": False, "error": "same signer key used twice"}

    first = verify(path_a, key_a, "operator" if a["role"] == "operator" else "reviewer")
    second = verify(path_b, key_b, "reviewer" if b["role"] == "reviewer" else "operator")

    approved = bool(first.get("verified") and second.get("verified"))
    return {
        "approved": approved,
        "operation_id": a["operation_id"],
        "action": a["action"],
        "epoch": a["epoch"],
        "operator_verified": first if a["role"] == "operator" else second,
        "reviewer_verified": second if b["role"] == "reviewer" else first,
    }

def break_glass(action: str, reason: str, ttl_minutes: int) -> dict:
    if not reason.strip():
        raise SystemExit("DENY: break-glass requires a reason")

    record = {
        "event": "BREAK_GLASS",
        "id": str(uuid.uuid4()),
        "issued_at": stamp(now()),
        "expires_at": stamp(now() + timedelta(minutes=max(1, min(ttl_minutes, 15)))),
        "action": action,
        "reason": reason.strip(),
        "epoch": current_epoch(),
        "operator": os.environ.get("USER", "unknown"),
    }

    ledger = authority_dir() / "break-glass.jsonl"
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())

    return {"recorded": True, "record": record, "ledger": str(ledger)}

def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init-role")
    p_init.add_argument("role")

    p_sign = sub.add_parser("sign")
    p_sign.add_argument("role")
    p_sign.add_argument("action")
    p_sign.add_argument("payload")
    p_sign.add_argument("--ttl-minutes", type=int, default=10)

    p_verify = sub.add_parser("verify")
    p_verify.add_argument("operation")
    p_verify.add_argument("trusted_public")

    p_quorum = sub.add_parser("quorum")
    p_quorum.add_argument("operator_operation")
    p_quorum.add_argument("reviewer_operation")
    p_quorum.add_argument("operator_public")
    p_quorum.add_argument("reviewer_public")

    sub.add_parser("advance-epoch")

    p_bg = sub.add_parser("break-glass")
    p_bg.add_argument("action")
    p_bg.add_argument("reason")
    p_bg.add_argument("--ttl-minutes", type=int, default=5)

    args = parser.parse_args()

    if args.command == "init-role":
        print(json.dumps(init_role(args.role), sort_keys=True))
    elif args.command == "sign":
        print(json.dumps(sign(args.role, args.action, json.loads(args.payload), args.ttl_minutes), sort_keys=True))
    elif args.command == "verify":
        result = verify(args.operation, args.trusted_public)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["verified"] else 1
    elif args.command == "quorum":
        result = quorum(args.operator_operation, args.reviewer_operation, args.operator_public, args.reviewer_public)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["approved"] else 1
    elif args.command == "advance-epoch":
        print(json.dumps({"epoch": advance_epoch()}, sort_keys=True))
    elif args.command == "break-glass":
        print(json.dumps(break_glass(args.action, args.reason, args.ttl_minutes), sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
