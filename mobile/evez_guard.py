#!/usr/bin/env python3
"""Defensive operator guard for EVEZ-OS.

Capabilities:
- local device key bootstrap using OpenSSL Ed25519
- signed operation envelopes
- signature verification
- fail-closed policy enforcement
- repository secret-pattern audit
- deterministic tracked-file manifest

This is an engineering control, not a claim of military certification or
hardware-backed attestation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SECURITY = ROOT / "security"
DEFAULT_DEVICE_DIR = Path.home() / ".config" / "evez" / "device"
POLICY_PATH = SECURITY / "mobile-policy.json"

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bASIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-(?:proj-|live-|test-)?[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"(?i)\b(?:aws_secret_access_key|private_key|client_secret)\s*[:=]\s*['\"]?[^\s'\"]{12,}"),
]

def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def device_dir() -> Path:
    value = os.environ.get("EVEZ_DEVICE_DIR")
    path = Path(value) if value else DEFAULT_DEVICE_DIR
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)
    return path

def run(cmd: list[str], *, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(cmd, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

def policy() -> dict:
    with POLICY_PATH.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise SystemExit("policy must be a JSON object")
    return value

def init_device() -> dict:
    directory = device_dir()
    private = directory / "ed25519-private.pem"
    public = directory / "ed25519-public.pem"

    if private.exists() or public.exists():
        return {"initialized": False, "reason": "device key already exists", "public_key": str(public)}

    generated = run(["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private)])
    if generated.returncode != 0:
        raise SystemExit(generated.stderr.decode("utf-8", "replace"))

    exported = run(["openssl", "pkey", "-in", str(private), "-pubout", "-out", str(public)])
    if exported.returncode != 0:
        private.unlink(missing_ok=True)
        raise SystemExit(exported.stderr.decode("utf-8", "replace"))

    os.chmod(private, 0o600)
    os.chmod(public, 0o644)
    return {
        "initialized": True,
        "public_key": str(public),
        "private_key": str(private),
        "note": "File-backed identity; not hardware-backed attestation.",
    }

def authorize(action: str, payload_text: str) -> dict:
    cfg = policy()
    actions = cfg.get("actions", {})
    if action not in actions:
        raise SystemExit(f"DENY: action not allowlisted: {action}")

    payload = json.loads(payload_text)
    payload_bytes = canonical(payload)
    max_bytes = int(actions[action].get("max_payload_bytes", 65536))
    if len(payload_bytes) > max_bytes:
        raise SystemExit(f"DENY: payload exceeds {max_bytes} bytes")

    required_env = actions[action].get("required_env", [])
    missing = [name for name in required_env if os.environ.get(name) != "1"]
    if missing:
        raise SystemExit("DENY: missing approvals: " + ",".join(missing))

    directory = device_dir()
    private = directory / "ed25519-private.pem"
    if not private.exists():
        raise SystemExit("DENY: device key absent; run init-device")

    envelope = {
        "version": 1,
        "operation_id": str(uuid.uuid4()),
        "issued_at": now(),
        "action": action,
        "payload": payload,
    }
    message = canonical(envelope)

    with tempfile.TemporaryDirectory() as tmp:
        message_path = Path(tmp) / "message.bin"
        signature_path = Path(tmp) / "signature.bin"
        message_path.write_bytes(message)

        signed = run([
            "openssl", "pkeyutl", "-sign", "-inkey", str(private),
            "-rawin", "-in", str(message_path), "-out", str(signature_path)
        ])
        if signed.returncode != 0:
            raise SystemExit(signed.stderr.decode("utf-8", "replace"))

        signature = signature_path.read_bytes().hex()

    result = {
        "envelope": envelope,
        "signature_hex": signature,
        "public_key": str(directory / "ed25519-public.pem"),
        "message_sha256": hashlib.sha256(message).hexdigest(),
    }
    return result

def verify_operation(path_text: str) -> dict:
    path = Path(path_text)
    value = json.loads(path.read_text(encoding="utf-8"))
    for key in ("envelope", "signature_hex", "public_key", "message_sha256"):
        if key not in value:
            raise SystemExit(f"invalid operation envelope: missing {key}")

    message = canonical(value["envelope"])
    expected = hashlib.sha256(message).hexdigest()
    if expected != value["message_sha256"]:
        return {"verified": False, "error": "message digest mismatch"}

    signature = bytes.fromhex(value["signature_hex"])
    with tempfile.TemporaryDirectory() as tmp:
        message_path = Path(tmp) / "message.bin"
        signature_path = Path(tmp) / "signature.bin"
        message_path.write_bytes(message)
        signature_path.write_bytes(signature)

        result = run([
            "openssl", "pkeyutl", "-verify", "-pubin",
            "-inkey", value["public_key"], "-rawin",
            "-in", str(message_path), "-sigfile", str(signature_path)
        ])

    return {
        "verified": result.returncode == 0,
        "operation_id": value["envelope"].get("operation_id"),
        "action": value["envelope"].get("action"),
        "message_sha256": expected,
    }

def tracked_files() -> list[Path]:
    result = run(["git", "-C", str(ROOT), "ls-files", "-z"])
    if result.returncode != 0:
        raise SystemExit(result.stderr.decode("utf-8", "replace"))
    names = [x for x in result.stdout.decode("utf-8").split("\0") if x]
    return [ROOT / name for name in names]

def secret_audit() -> dict:
    findings: list[dict] = []
    for path in tracked_files():
        if not path.is_file():
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if len(data) > 8 * 1024 * 1024:
            continue
        text = data.decode("utf-8", "ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append({"file": str(path.relative_to(ROOT)), "pattern": pattern.pattern})
    return {"clean": not findings, "findings": findings}

def manifest() -> dict:
    files = []
    for path in tracked_files():
        if not path.is_file():
            continue
        files.append({
            "path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size,
        })
    files.sort(key=lambda row: row["path"])
    document = {
        "version": 1,
        "generated_at": now(),
        "git_commit": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
        "files": files,
    }
    document["manifest_sha256"] = hashlib.sha256(canonical(document)).hexdigest()
    return document

def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init-device")

    p_auth = sub.add_parser("authorize")
    p_auth.add_argument("action")
    p_auth.add_argument("payload")

    p_verify = sub.add_parser("verify-operation")
    p_verify.add_argument("path")
    sub.add_parser("secret-audit")
    sub.add_parser("manifest")

    args = parser.parse_args()

    if args.command == "init-device":
        print(json.dumps(init_device(), sort_keys=True))
        return 0

    if args.command == "authorize":
        result = authorize(args.action, args.payload)
        out = device_dir() / "operations" / f"{result['envelope']['operation_id']}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        os.chmod(out, 0o600)
        result["saved_to"] = str(out)
        print(json.dumps(result, sort_keys=True))
        return 0

    if args.command == "verify-operation":
        result = verify_operation(args.path)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["verified"] else 1

    if args.command == "secret-audit":
        result = secret_audit()
        print(json.dumps(result, sort_keys=True))
        return 0 if result["clean"] else 1

    if args.command == "manifest":
        print(json.dumps(manifest(), sort_keys=True, indent=2))
        return 0

    return 2

if __name__ == "__main__":
    raise SystemExit(main())
