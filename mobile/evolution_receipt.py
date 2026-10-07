#!/usr/bin/env python3
"""Bounded, deterministic receipts for EVEZ self-evolution experiments.

Receipts are evidence containers, not truth claims. This module can capture
provenance from a live git checkout and can verify a receipt against that
checkout, but it never promotes or deploys anything.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
STATUSES = {"PROPOSED", "UNKNOWN", "VERIFIED", "REJECTED"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_FIELDS = {
    "schema_version",
    "source_commit",
    "working_tree_state",
    "test_manifest",
    "test_results",
    "evidence_input_digests",
    "proposal_digest",
    "contradiction_cases",
    "failed_attempts",
    "uncertainties",
    "dissenting_observations",
    "verification_status",
    "verification_timestamp",
    "receipt_digest",
}


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def bytes_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _require_hex(
    name: str, value: Any, pattern: re.Pattern[str], errors: list[str]
) -> None:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        errors.append(f"{name}: invalid digest")


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            f"git {' '.join(args)} failed: {result.stderr.strip() or 'unknown error'}"
        )
    return result.stdout.strip()


def _working_tree(root: Path) -> dict[str, Any]:
    dirty_output = _git(
        root, "status", "--porcelain", "--untracked-files=all"
    )
    return {"clean": not bool(dirty_output)}


def _capture_files(root: Path, paths: list[str]) -> list[dict[str, str]]:
    captured: list[dict[str, str]] = []
    seen: set[str] = set()
    for relative in paths:
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
            raise ValueError(f"invalid repository-relative path: {relative!r}")
        normalized = Path(relative).as_posix()
        if normalized in seen:
            raise ValueError(f"duplicate repository path: {normalized}")
        seen.add(normalized)
        target = (root / normalized).resolve()
        root_resolved = root.resolve()
        if root_resolved not in target.parents:
            raise ValueError(f"path escapes checkout: {normalized}")
        if target.is_symlink():
            raise ValueError(f"symbolic links are not allowed in receipt capture: {normalized}")
        if not target.is_file():
            raise ValueError(f"repository file not found: {normalized}")
        captured.append(
            {"path": normalized, "sha256": bytes_digest(target.read_bytes())}
        )
    return captured


def capture_spec(spec: dict[str, Any], root: Path) -> dict[str, Any]:
    root = root.resolve()
    if not (root / ".git").exists():
        raise ValueError(f"not a git checkout: {root}")

    working = spec.get("working_tree_state")
    if not isinstance(working, dict):
        raise ValueError("working_tree_state must be an object in capture input")
    paths = working.get("files")
    if not isinstance(paths, list):
        raise ValueError("working_tree_state.files must be a list in capture input")

    relative_paths: list[str] = []
    for item in paths:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise ValueError("capture input contains an invalid working-tree file entry")
        relative_paths.append(item["path"])

    captured = dict(spec)
    captured["source_commit"] = _git(root, "rev-parse", "HEAD")
    captured["working_tree_state"] = {
        **_working_tree(root),
        "files": _capture_files(root, relative_paths),
    }
    captured["verification_status"] = (
        "PROPOSED"
        if captured.get("verification_status") == "VERIFIED"
        else captured.get("verification_status", "PROPOSED")
    )
    captured["verification_timestamp"] = now()
    return captured


def validate(receipt: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    errors: list[str] = []

    missing = sorted(REQUIRED_FIELDS - set(receipt))
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")

    if receipt.get("schema_version") != SCHEMA_VERSION:
        errors.append("unsupported schema_version")

    _require_hex("source_commit", receipt.get("source_commit"), GIT_SHA_RE, errors)
    _require_hex("proposal_digest", receipt.get("proposal_digest"), SHA256_RE, errors)
    _require_hex("receipt_digest", receipt.get("receipt_digest"), SHA256_RE, errors)

    if receipt.get("verification_status") not in STATUSES:
        errors.append("invalid verification_status")

    working = receipt.get("working_tree_state")
    if not isinstance(working, dict):
        errors.append("working_tree_state must be an object")
    else:
        if not isinstance(working.get("clean"), bool):
            errors.append("working_tree_state.clean must be boolean")
        files = working.get("files")
        if not isinstance(files, list):
            errors.append("working_tree_state.files must be a list")
        else:
            seen: set[str] = set()
            for item in files:
                if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                    errors.append("working_tree_state.files contains invalid entry")
                    continue
                path = item["path"]
                if path in seen:
                    errors.append(f"duplicate working-tree path: {path}")
                seen.add(path)
                _require_hex(
                    f"working_tree_state.files[{path}]",
                    item.get("sha256"),
                    SHA256_RE,
                    errors,
                )

    evidence = receipt.get("evidence_input_digests")
    if not isinstance(evidence, dict):
        errors.append("evidence_input_digests must be an object")
    else:
        for label, value in evidence.items():
            _require_hex(f"evidence_input_digests[{label}]", value, SHA256_RE, errors)

    tests = receipt.get("test_manifest")
    results = receipt.get("test_results")
    if not isinstance(tests, list) or not isinstance(results, list):
        errors.append("test_manifest and test_results must be lists")
        tests = tests if isinstance(tests, list) else []
        results = results if isinstance(results, list) else []

    manifest_by_id: dict[str, dict[str, Any]] = {}
    for item in tests:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            errors.append("invalid test_manifest entry")
            continue
        test_id = item["id"]
        if test_id in manifest_by_id:
            errors.append(f"duplicate test id: {test_id}")
        manifest_by_id[test_id] = item
        command = item.get("command")
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(part, str) for part in command)
        ):
            errors.append(f"test {test_id}: command must be a non-empty argv list")
        if not isinstance(item.get("expected_exit_code"), int):
            errors.append(f"test {test_id}: expected_exit_code must be int")

    result_by_id: dict[str, dict[str, Any]] = {}
    for item in results:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            errors.append("invalid test_results entry")
            continue
        test_id = item["id"]
        if test_id in result_by_id:
            errors.append(f"duplicate test result id: {test_id}")
        result_by_id[test_id] = item
        if test_id not in manifest_by_id:
            errors.append(f"orphan test result: {test_id}")
            continue
        if not isinstance(item.get("exit_code"), int):
            errors.append(f"test {test_id}: exit_code must be int")
        for field in ("stdout_sha256", "stderr_sha256"):
            _require_hex(
                f"test_results[{test_id}].{field}",
                item.get(field),
                SHA256_RE,
                errors,
            )
        expected = manifest_by_id[test_id].get("expected_exit_code")
        derived = "PASS" if item.get("exit_code") == expected else "FAIL"
        if item.get("status") != derived:
            errors.append(f"test {test_id}: status does not match exit code")

    missing_results = sorted(set(manifest_by_id) - set(result_by_id))
    if missing_results:
        errors.append("missing test results: " + ", ".join(missing_results))

    contradictions = receipt.get("contradiction_cases")
    if not isinstance(contradictions, list):
        errors.append("contradiction_cases must be a list")
        contradictions = []
    unresolved = 0
    for index, item in enumerate(contradictions):
        if not isinstance(item, dict):
            errors.append(f"contradiction_cases[{index}] must be an object")
            continue
        for field in ("id", "claim", "falsifier", "resolution"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"contradiction_cases[{index}].{field} missing")
        if not isinstance(item.get("resolved"), bool):
            errors.append(f"contradiction_cases[{index}].resolved must be boolean")
        elif not item["resolved"]:
            unresolved += 1

    for field in ("failed_attempts", "uncertainties", "dissenting_observations"):
        if not isinstance(receipt.get(field), list):
            errors.append(f"{field} must be a list")

    unsigned = dict(receipt)
    unsigned.pop("receipt_digest", None)
    computed_receipt_digest = digest(unsigned)
    if receipt.get("receipt_digest") != computed_receipt_digest:
        errors.append("receipt_digest mismatch")

    test_failures = [
        test_id for test_id, item in result_by_id.items() if item.get("status") != "PASS"
    ]
    claimed = receipt.get("verification_status")
    working_clean = working.get("clean", False) if isinstance(working, dict) else False
    promotion_eligible = (
        claimed == "VERIFIED"
        and not errors
        and not test_failures
        and unresolved == 0
        and len(result_by_id) == len(manifest_by_id)
        and working_clean is True
    )

    result = {
        "integrity_verified": not errors,
        "promotion_eligible": promotion_eligible,
        "verification_status": claimed,
        "test_failures": test_failures,
        "unresolved_contradictions": unresolved,
        "errors": errors,
        "preserved_evidence": {
            "failed_attempts": len(receipt.get("failed_attempts", []))
            if isinstance(receipt.get("failed_attempts"), list)
            else 0,
            "uncertainties": len(receipt.get("uncertainties", []))
            if isinstance(receipt.get("uncertainties"), list)
            else 0,
            "dissenting_observations": len(receipt.get("dissenting_observations", []))
            if isinstance(receipt.get("dissenting_observations"), list)
            else 0,
        },
    }
    return not errors, result


def verify_against(receipt: dict[str, Any], root: Path) -> tuple[bool, dict[str, Any]]:
    ok, details = validate(receipt)
    errors = list(details["errors"])
    root = root.resolve()

    try:
        if not (root / ".git").exists():
            raise ValueError(f"not a git checkout: {root}")

        actual_commit = _git(root, "rev-parse", "HEAD")
        actual_clean = _working_tree(root)["clean"]

        if actual_commit != receipt.get("source_commit"):
            errors.append(
                f"source commit mismatch: receipt={receipt.get('source_commit')} actual={actual_commit}"
            )

        expected_clean = working.get("clean") if isinstance(working, dict) else None
        if isinstance(expected_clean, bool) and expected_clean != actual_clean:
            errors.append(
                f"working tree cleanliness mismatch: receipt={expected_clean} actual={actual_clean}"
            )

        working = receipt.get("working_tree_state")
        file_entries = working.get("files", []) if isinstance(working, dict) else []
        for item in file_entries:
            relative = item.get("path")
            if not isinstance(relative, str):
                continue
            target = root / relative
            if not target.is_file():
                errors.append(f"missing repository file: {relative}")
                continue
            actual_hash = bytes_digest(target.read_bytes())
            if actual_hash != item.get("sha256"):
                errors.append(
                    f"file digest mismatch: {relative} receipt={item.get('sha256')} actual={actual_hash}"
                )
    except (OSError, ValueError) as exc:
        errors.append(str(exc))

    details = dict(details)
    details["environment_match"] = not errors
    details["errors"] = errors
    details["integrity_verified"] = not errors
    details["promotion_eligible"] = bool(details["promotion_eligible"] and not errors)
    return not errors and ok, details


def build(spec: dict[str, Any]) -> dict[str, Any]:
    required = REQUIRED_FIELDS - {"receipt_digest", "verification_timestamp", "schema_version"}
    missing = sorted(required - set(spec))
    if missing:
        raise ValueError("missing spec fields: " + ", ".join(missing))

    status = spec["verification_status"]
    if status == "VERIFIED":
        raise ValueError(
            "build refuses to create a VERIFIED receipt; independent verification must set promotion state"
        )
    if status not in STATUSES:
        raise ValueError("invalid verification_status")

    receipt = {
        "schema_version": SCHEMA_VERSION,
        **{
            key: spec[key]
            for key in REQUIRED_FIELDS
            if key not in {"schema_version", "verification_timestamp", "receipt_digest"}
        },
        "verification_timestamp": spec.get("verification_timestamp") or now(),
    }
    receipt["receipt_digest"] = digest(receipt)
    ok, details = validate(receipt)
    if not ok:
        raise ValueError(
            "generated receipt failed validation: " + "; ".join(details["errors"])
        )
    return receipt


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("receipt/spec must be a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def cmd_capture(root: Path, input_path: Path, output_path: Path) -> int:
    captured = capture_spec(load(input_path), root)
    write_json(output_path, captured)
    print(
        json.dumps(
            {
                "captured": True,
                "source_commit": captured["source_commit"],
                "clean": captured["working_tree_state"]["clean"],
                "files": len(captured["working_tree_state"]["files"]),
            },
            sort_keys=True,
        )
    )
    return 0


def cmd_build(input_path: Path, output_path: Path) -> int:
    receipt = build(load(input_path))
    write_json(output_path, receipt)
    print(
        json.dumps(
            {
                "built": True,
                "status": receipt["verification_status"],
                "receipt_digest": receipt["receipt_digest"],
            },
            sort_keys=True,
        )
    )
    return 0


def cmd_verify(path: Path) -> int:
    receipt = load(path)
    _, details = validate(receipt)
    print(json.dumps(details, indent=2, sort_keys=True))
    return 0 if details["integrity_verified"] else 1


def cmd_verify_against(path: Path, root: Path) -> int:
    receipt = load(path)
    _, details = verify_against(receipt, root)
    print(json.dumps(details, indent=2, sort_keys=True))
    return 0 if details["integrity_verified"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build, capture, and verify bounded EVEZ evolution receipts."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    capture_parser = sub.add_parser("capture")
    capture_parser.add_argument("root")
    capture_parser.add_argument("input")
    capture_parser.add_argument("output")

    build_parser = sub.add_parser("build")
    build_parser.add_argument("input")
    build_parser.add_argument("output")

    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("receipt")

    against_parser = sub.add_parser("verify-against")
    against_parser.add_argument("receipt")
    against_parser.add_argument("root")

    args = parser.parse_args()

    try:
        if args.command == "capture":
            return cmd_capture(Path(args.root), Path(args.input), Path(args.output))
        if args.command == "build":
            return cmd_build(Path(args.input), Path(args.output))
        if args.command == "verify":
            return cmd_verify(Path(args.receipt))
        return cmd_verify_against(Path(args.receipt), Path(args.root))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"verified": False, "error": str(exc)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
