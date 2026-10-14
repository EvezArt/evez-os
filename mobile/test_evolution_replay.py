#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RECEIPT = ROOT / "evolution_receipt.py"
REPLAY = ROOT / "evolution_replay.py"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def git(cwd: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(cwd), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, (args, result.stdout, result.stderr)


def run_replay(receipt: Path, repo: Path, expect: int = 0):
    result = subprocess.run(
        [sys.executable, str(REPLAY), str(receipt), str(repo)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == expect, (result.stdout, result.stderr)
    return json.loads(result.stdout)


with tempfile.TemporaryDirectory() as temp:
    temp_path = Path(temp)
    repo = temp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "replay-test")

    script = repo / "fixture.py"
    script.write_text(
        "import os\nprint('stable')\nassert 'API_KEY' not in os.environ\n",
        encoding="utf-8",
    )
    git(repo, "add", "fixture.py")
    git(repo, "commit", "-m", "fixture")

    commit = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()

    spec = {
        "schema_version": 1,
        "source_commit": commit,
        "working_tree_state": {
            "clean": True,
            "files": [
                {"path": "fixture.py", "sha256": sha(script.read_bytes())}
            ],
        },
        "test_manifest": [
            {
                "id": "fixture",
                "command": ["python", "fixture.py"],
                "expected_exit_code": 0,
            }
        ],
        "test_results": [],
        "evidence_input_digests": {"fixture": sha(b"fixture")},
        "proposal_digest": sha(canonical({"task": "replay"})),
        "contradiction_cases": [
            {
                "id": "r-001",
                "claim": "replay is reproducible",
                "falsifier": "two runs yield different hashes",
                "resolution": "must report FAIL",
                "resolved": True,
            }
        ],
        "failed_attempts": ["none yet"],
        "uncertainties": ["replay environment may differ across devices"],
        "dissenting_observations": ["determinism does not prove semantic correctness"],
        "verification_status": "PROPOSED",
        "verification_timestamp": "2026-10-07T00:00:00Z",
    }
    spec_path = temp_path / "spec.json"
    capture_path = temp_path / "captured.json"
    receipt_path = temp_path / "receipt.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")

    capture = subprocess.run(
        [
            sys.executable,
            str(RECEIPT),
            "capture",
            str(repo),
            str(spec_path),
            str(capture_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert capture.returncode == 0, (capture.stdout, capture.stderr)

    captured = json.loads(capture_path.read_text(encoding="utf-8"))
    captured["test_results"] = [
        {
            "id": "fixture",
            "exit_code": 0,
            "stdout_sha256": sha(b"stable\n"),
            "stderr_sha256": sha(b""),
            "status": "PASS",
        }
    ]

    build = subprocess.run(
        [sys.executable, str(RECEIPT), "build", str(capture_path), str(receipt_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert build.returncode == 0, (build.stdout, build.stderr)

    report = run_replay(receipt_path, repo)
    assert report["replay_status"] == "PASS"
    assert report["promotion_eligible"] is False
    assert report["runs"][0]["deterministic"] is True

    tampered = repo / "fixture.py"
    tampered.write_text(
        "import os\nprint('changed')\nassert 'API_KEY' not in os.environ\n",
        encoding="utf-8",
    )
    failed = run_replay(receipt_path, repo, expect=1)
    assert failed["replay_status"] == "UNVERIFIED"
    assert failed["environment_match"] is False

    # Ensure the runner refuses shell commands instead of turning a receipt
    # into an arbitrary command-execution primitive.
    git(repo, "checkout", "--", "fixture.py")
    shell_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    shell_receipt["test_manifest"][0]["command"] = ["bash", "-c", "echo pwned"]
    shell_unsigned = dict(shell_receipt)
    shell_unsigned.pop("receipt_digest")
    shell_receipt["receipt_digest"] = sha(canonical(shell_unsigned))
    shell_path = temp_path / "shell.json"
    shell_path.write_text(json.dumps(shell_receipt), encoding="utf-8")
    refused = run_replay(shell_path, repo, expect=1)
    assert refused["replay_status"] == "FAIL"
    assert any("only Python test scripts" in item for item in refused["errors"])

print("evolution replay reproducibility + sandbox tests: PASS")
