#!/usr/bin/env python3
"""Offline-safe replay runner for EVEZ evolution receipts.

It re-executes only explicit Python-script test commands from a receipt,
with a sanitized environment, bounded output capture, and two-run
determinism checking. It never promotes a receipt to VERIFIED.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from evolution_receipt import load, verify_against

MAX_DEFAULT_OUTPUT = 64 * 1024
PYTHON_NAMES = {"python", "python3", Path(sys.executable).name}
SENSITIVE_ENV_MARKERS = (
    "SECRET",
    "TOKEN",
    "PASSWORD",
    "CREDENTIAL",
    "PRIVATE_KEY",
    "AUTH",
    "API_KEY",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_env(root: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    for key in ("PATH", "LANG", "LC_ALL", "TMPDIR"):
        value = os.environ.get(key)
        if value:
            env[key] = value
    env["HOME"] = tempfile.gettempdir()
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    env["EVEZ_REPLAY_ROOT"] = str(root)
    for key in list(env):
        upper = key.upper()
        if any(marker in upper for marker in SENSITIVE_ENV_MARKERS):
            env.pop(key, None)
    return env


def validate_command(command: Any, root: Path) -> list[str]:
    if (
        not isinstance(command, list)
        or not command
        or not all(isinstance(part, str) and part for part in command)
    ):
        raise ValueError("replay only accepts non-empty argv lists")

    if command[0] not in PYTHON_NAMES:
        raise ValueError("replay accepts only Python test scripts")

    if len(command) < 2:
        raise ValueError("python replay command requires a script path")

    script = Path(command[1])
    if script.is_absolute() or script.suffix != ".py":
        raise ValueError("replay script must be a relative .py path")

    target = (root / script).resolve()
    root_resolved = root.resolve()
    if root_resolved not in target.parents:
        raise ValueError("replay script escapes checkout")
    if not target.is_file():
        raise ValueError(f"replay script not found: {script.as_posix()}")

    if any(part.startswith("-") for part in command[1:2]):
        raise ValueError("replay does not allow interpreter options")

    return [sys.executable, script.as_posix(), *command[2:]]


def run_once(
    root: Path, command: list[str], max_output: int
) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=root,
        env=safe_env(root),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
        check=False,
    )
    stdout = completed.stdout
    stderr = completed.stderr
    bounded = len(stdout) <= max_output and len(stderr) <= max_output
    return {
        "exit_code": completed.returncode,
        "stdout_sha256": sha(stdout),
        "stderr_sha256": sha(stderr),
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
        "bounded_output": bounded,
    }


def compare_run(
    expected: dict[str, Any], actual: dict[str, Any], run_id: str
) -> list[str]:
    errors: list[str] = []
    for field in ("exit_code", "stdout_sha256", "stderr_sha256"):
        if expected.get(field) != actual.get(field):
            errors.append(
                f"{run_id}: {field} mismatch expected={expected.get(field)} actual={actual.get(field)}"
            )
    if actual.get("status") == "FAIL":
        errors.append(f"{run_id}: declared test result is FAIL")
    return errors


def replay(root: Path, receipt: dict[str, Any], max_output: int) -> dict[str, Any]:
    ok, provenance = verify_against(receipt, root)
    if not ok:
        return {
            "replay_status": "UNVERIFIED",
            "environment_match": False,
            "errors": provenance["errors"],
            "runs": [],
            "environment": environment_report(root),
        }

    manifest = {
        item["id"]: item
        for item in receipt.get("test_manifest", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    results = {
        item["id"]: item
        for item in receipt.get("test_results", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    errors: list[str] = []
    runs: list[dict[str, Any]] = []

    for test_id, item in manifest.items():
        if test_id not in results:
            errors.append(f"missing recorded result: {test_id}")
            continue
        try:
            command = validate_command(item.get("command"), root)
            first = run_once(root, command, max_output)
            second = run_once(root, command, max_output)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            errors.append(f"{test_id}: replay error: {exc}")
            continue

        deterministic = first == second
        expected = results[test_id]
        expected_errors = compare_run(expected, first, test_id)
        if not deterministic:
            errors.append(f"{test_id}: nondeterministic replay result")
        if not first["bounded_output"]:
            errors.append(f"{test_id}: output bound exceeded")
        errors.extend(expected_errors)
        runs.append(
            {
                "id": test_id,
                "deterministic": deterministic,
                "first": first,
                "second": second,
                "expected": {
                    key: expected.get(key)
                    for key in ("exit_code", "stdout_sha256", "stderr_sha256", "status")
                },
            }
        )

    status = "PASS" if not errors else "FAIL"
    return {
        "replay_status": status,
        "environment_match": True,
        "promotion_eligible": False,
        "errors": errors,
        "runs": runs,
        "environment": environment_report(root),
    }


def environment_report(root: Path) -> dict[str, str]:
    return {
        "python": sys.version.split()[0],
        "python_executable": str(Path(sys.executable).resolve()),
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "checkout": str(root.resolve()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay a bounded EVEZ evolution receipt offline."
    )
    parser.add_argument("receipt")
    parser.add_argument("root")
    parser.add_argument(
        "--max-output",
        type=int,
        default=MAX_DEFAULT_OUTPUT,
        help="maximum captured stdout/stderr bytes per stream",
    )
    args = parser.parse_args()

    if args.max_output <= 0:
        parser.error("--max-output must be positive")

    try:
        report = replay(Path(args.root), load(Path(args.receipt)), args.max_output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report = {
            "replay_status": "UNVERIFIED",
            "promotion_eligible": False,
            "errors": [str(exc)],
            "runs": [],
        }

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["replay_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
