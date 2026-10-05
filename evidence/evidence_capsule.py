#!/usr/bin/env python3
"""Portable evidence capsule builder and verifier.

A capsule is an immutable-style JSON container whose embedded artifacts retain
their original bytes, encoding, size, and SHA-256 digest. Verification checks
both every artifact and the capsule digest.

The capsule is a transport and provenance format. It does not make claims true.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()

def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def read_artifact(name: str, path: str) -> dict:
    source = Path(path)
    if not source.is_file():
        raise SystemExit(f"artifact not found: {path}")
    raw = source.read_bytes()
    media_type = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
    digest = sha256_bytes(raw)
    try:
        text = raw.decode("utf-8")
        encoding = "utf-8"
        content = text
    except UnicodeDecodeError:
        encoding = "base64"
        content = base64.b64encode(raw).decode("ascii")
    return {
        "name": name,
        "path": str(source),
        "media_type": media_type,
        "encoding": encoding,
        "size": len(raw),
        "sha256": digest,
        "content": content,
    }

def artifact_pairs(items: list[str]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for item in items:
        if "=" not in item:
            raise SystemExit("artifacts must use NAME=PATH form")
        name, path = item.split("=", 1)
        name, path = name.strip(), path.strip()
        if not name or not path:
            raise SystemExit("artifact names and paths must be non-empty")
        pairs.append((name, path))
    if not pairs:
        raise SystemExit("at least one artifact is required")
    return pairs

def build(pairs: list[tuple[str, str]], metadata: dict | None = None) -> dict:
    artifacts = [read_artifact(name, path) for name, path in pairs]
    manifest = [
        {
            "name": row["name"],
            "path": row["path"],
            "media_type": row["media_type"],
            "encoding": row["encoding"],
            "size": row["size"],
            "sha256": row["sha256"],
        }
        for row in artifacts
    ]
    capsule = {
        "schema_version": 1,
        "capsule_type": "EVEZ_EVIDENCE_CAPSULE",
        "created_at": now(),
        "metadata": metadata or {},
        "artifact_count": len(artifacts),
        "manifest": manifest,
        "artifacts": artifacts,
        "epistemic_rule": "CAPSULE_INTEGRITY != CLAIM_TRUTH != EXPLANATION",
        "capsule_sha256": None,
    }
    capsule["capsule_sha256"] = sha256_bytes(canonical(capsule))
    return capsule

def verify(capsule: dict) -> dict:
    required = {"schema_version", "capsule_type", "artifact_count", "manifest", "artifacts", "capsule_sha256"}
    missing = sorted(required.difference(capsule))
    if missing:
        return {"verified": False, "error": "missing_fields", "fields": missing}
    if capsule["schema_version"] != 1:
        return {"verified": False, "error": "unsupported_schema_version", "actual": capsule["schema_version"]}
    if capsule["capsule_type"] != "EVEZ_EVIDENCE_CAPSULE":
        return {"verified": False, "error": "wrong_capsule_type"}
    artifacts, manifest = capsule["artifacts"], capsule["manifest"]
    if not isinstance(artifacts, list) or not isinstance(manifest, list):
        return {"verified": False, "error": "manifest_or_artifacts_not_lists"}
    if len(artifacts) != capsule["artifact_count"] or len(manifest) != capsule["artifact_count"]:
        return {"verified": False, "error": "artifact_count_mismatch"}

    errors: list[dict] = []
    for index, artifact in enumerate(artifacts):
        try:
            if artifact["encoding"] == "utf-8":
                raw = artifact["content"].encode("utf-8")
            elif artifact["encoding"] == "base64":
                raw = base64.b64decode(artifact["content"], validate=True)
            else:
                raise ValueError("unsupported encoding")
            actual = sha256_bytes(raw)
        except Exception as exc:
            errors.append({"index": index, "error": "artifact_decode_failed", "detail": str(exc)})
            continue

        if actual != artifact.get("sha256"):
            errors.append({
                "index": index,
                "name": artifact.get("name"),
                "error": "artifact_hash_mismatch",
                "expected": artifact.get("sha256"),
                "actual": actual,
            })
        manifest_row = manifest[index]
        for key in ("name", "media_type", "encoding", "size", "sha256"):
            if artifact.get(key) != manifest_row.get(key):
                errors.append({
                    "index": index,
                    "name": artifact.get("name"),
                    "error": "manifest_mismatch",
                    "field": key,
                })

    unsigned = dict(capsule)
    unsigned["capsule_sha256"] = None
    expected_capsule = sha256_bytes(canonical(unsigned))
    if expected_capsule != capsule["capsule_sha256"]:
        errors.append({
            "error": "capsule_hash_mismatch",
            "expected": expected_capsule,
            "actual": capsule["capsule_sha256"],
        })
    return {
        "verified": not errors,
        "artifact_count": len(artifacts),
        "capsule_sha256": capsule["capsule_sha256"],
        "errors": errors,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("output")
    build_parser.add_argument("artifacts", nargs="+")
    build_parser.add_argument("--metadata")
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("capsule")
    args = parser.parse_args()

    if args.command == "build":
        metadata = json.loads(args.metadata) if args.metadata else {}
        result = build(artifact_pairs(args.artifacts), metadata)
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({
            "built": True,
            "output": args.output,
            "artifact_count": result["artifact_count"],
            "capsule_sha256": result["capsule_sha256"],
        }, sort_keys=True))
        return 0

    capsule = json.loads(Path(args.capsule).read_text(encoding="utf-8"))
    result = verify(capsule)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verified"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
