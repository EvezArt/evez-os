#!/usr/bin/env python3
"""Run deterministic, offline checks and emit a bounded witness report."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evez_possibility_witness_loop import (  # noqa: E402
    authorize_handoff,
    canonical_json_bytes,
    evaluate_witness_receipt,
    ReplayGuard,
    validate_handoff,
    verify_artifact_digest,
)


def run_check(name, fn):
    try:
        detail = fn()
        passed = detail is True
        return {"name": name, "status": "PASS" if passed else "FAIL", "detail": "assertion passed" if passed else str(detail)}
    except Exception as exc:  # output must retain a failed check, not hide it
        return {"name": name, "status": "FAIL", "detail": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional path for the JSON witness report")
    args = parser.parse_args()

    envelope_path = ROOT / "examples/evez-handoff-v1.example.json"
    artifact_path = ROOT / "examples/fixtures/possibility-witness-artifact.txt"
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    artifact = artifact_path.read_bytes()
    now = datetime.now(timezone.utc)

    def handoff_valid():
        errors = validate_handoff(envelope, now=now)
        if errors:
            raise AssertionError("; ".join(errors))
        return True

    def artifact_digest_matches():
        return verify_artifact_digest(envelope["artifacts"][0]["sha256"], artifact)

    def readonly_gate_denies_write():
        decision = authorize_handoff(
            envelope,
            recipient=envelope["recipient"],
            granted_capabilities=envelope["requested_capabilities"],
            operation="write",
            read_only=True,
            now=now,
        )
        return decision["decision"] == "DENY" and "read_only_mode" in decision["reasons"] and not decision["execution_performed"]

    def duplicate_request_not_reexecuted():
        guard = ReplayGuard()
        first = guard.accept_once(envelope, now=now)
        replay = guard.accept_once(envelope, now=now)
        return first["decision"] == "ALLOW" and replay["decision"] == "DENY" and replay["reason"] == "replay_detected" and not replay["execution_performed"]

    def unsealed_result_is_not_success():
        decision = evaluate_witness_receipt(
            {"terminal": False, "result_status": "SUCCEEDED", "checks": {"schema": "PASS"}},
            required_checks=["schema"],
        )
        return decision["status"] == "blocked" and decision["reason"] == "missing_terminal_receipt"

    checks = [
        run_check("example_handoff_valid", handoff_valid),
        run_check("artifact_sha256_matches_fixture", artifact_digest_matches),
        run_check("read_only_gate_denies_write", readonly_gate_denies_write),
        run_check("duplicate_idempotency_key_not_reexecuted", duplicate_request_not_reexecuted),
        run_check("missing_terminal_receipt_not_promoted", unsealed_result_is_not_success),
    ]
    failed = [item for item in checks if item["status"] != "PASS"]
    report = {
        "schema": "EVEZ-Witness/1",
        "scope": "offline deterministic fixtures only",
        "created_at": now.isoformat().replace("+00:00", "Z"),
        "result_status": "FAILED" if failed else "SUCCEEDED",
        "verification_status": "blocked" if failed else "partially_verified",
        "independent_verifier": {"present": False, "identity": None},
        "checks": checks,
        "limitations": [
            "This report does not prove remote service connectivity or production health.",
            "It does not claim that a GitHub, Tailscale, BioNeMo, Product Design, or Ads Manager action was executed.",
            "The report generator is not an independent verifier; successful results remain partially verified until separate review.",
            "This fixture serializer is deterministic Python JSON, not a claim of RFC 8785 conformance.",
        ],
        "not_run": [
            "remote adapter connectivity",
            "production mutation tests",
            "full repository test suite",
            "independent external verification",
        ],
    }
    import hashlib
    report["integrity"] = {
        "algorithm": "sha256",
        "sha256": hashlib.sha256(canonical_json_bytes(report)).hexdigest(),
    }
    rendered = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    print(rendered, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
