#!/usr/bin/env python3
"""Machine-verifiable EVEZ runtime identity and self-witness surface."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IDENTITY_FILE = ROOT / "identity" / "evez.identity.json"

def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def identity_path() -> Path:
    value = os.environ.get("EVEZ_IDENTITY_FILE")
    return Path(value) if value else DEFAULT_IDENTITY_FILE


def state_dir() -> Path:
    value = os.environ.get("EVEZ_STATE_DIR")
    return Path(value) if value else Path.home() / ".local" / "state" / "evez"


def load_identity() -> tuple[dict[str, Any], bool, str]:
    path = identity_path()
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("evez") != "EVEZ" or value.get("version") != 1:
        return value, False, "invalid EVEZ identity marker or version"

    integrity = value.get("integrity")
    if not isinstance(integrity, dict) or not isinstance(integrity.get("sha256"), str):
        return value, False, "missing integrity.sha256"

    unsigned = {key: current for key, current in value.items() if key != "integrity"}
    actual = hashlib.sha256(canonical(unsigned)).hexdigest()
    expected = integrity["sha256"]
    if actual != expected:
        return value, False, "identity digest mismatch"

    return value, True, actual


def git_value(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), *args],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def evidence_status() -> dict[str, Any]:
    try:
        sys.path.insert(0, str(ROOT / "mobile"))
        import evez_state
        return evez_state.verify()
    except Exception as exc:
        return {"verified": False, "error": f"evidence verification unavailable: {exc}"}


def snapshot() -> dict[str, Any]:
    value, verified, digest = load_identity()
    return {
        "identity": {
            "verified": verified,
            "sha256": digest if verified else value.get("integrity", {}).get("sha256"),
            "source": str(identity_path()),
            "name": value.get("identity", {}).get("name"),
            "id": value.get("identity", {}).get("id"),
            "state": value.get("identity", {}).get("identity_state"),
        },
        "runtime": {
            "implementation": value.get("identity", {}).get("implementation"),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "executable": sys.executable,
            "git_head": git_value("rev-parse", "HEAD"),
            "git_dirty": bool(git_value("status", "--porcelain")),
        },
        "evidence": evidence_status(),
        "authority": value.get("authority", {}),
    }


def self_witness() -> dict[str, Any]:
    value, verified, digest = load_identity()
    if not verified:
        return {
            "recorded": False,
            "error": "refusing self-witness: identity is not verified",
        }

    evidence = evidence_status()
    if not evidence.get("verified"):
        return {
            "recorded": False,
            "error": "refusing self-witness: evidence chain is not verified",
            "evidence": evidence,
        }

    sys.path.insert(0, str(ROOT / "mobile"))
    import evez_state

    payload = {
        "identity_sha256": digest,
        "identity_id": value["identity"]["id"],
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "git_head": git_value("rev-parse", "HEAD"),
            "git_dirty": bool(git_value("status", "--porcelain")),
        },
        "authority": value["authority"],
        "evidence_head_before_witness": evidence.get("head", "GENESIS"),
    }
    result = evez_state.record("IDENTITY_SELF_WITNESS", payload, queue=False)
    return {
        "recorded": True,
        "event": result,
        "identity_sha256": digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify and witness the EVEZ runtime identity.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("verify")
    sub.add_parser("show")
    sub.add_parser("self-witness")
    args = parser.parse_args()

    try:
        if args.command == "verify":
            _, verified, digest = load_identity()
            result = {
                "verified": verified,
                "sha256": digest if verified else None,
                "source": str(identity_path()),
            }
            print(json.dumps(result, sort_keys=True))
            return 0 if verified else 1

        if args.command == "show":
            print(json.dumps(snapshot(), indent=2, sort_keys=True))
            return 0

        result = self_witness()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["recorded"] else 1

    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(json.dumps({"verified": False, "recorded": False, "error": str(exc)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
