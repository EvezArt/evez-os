"""Read, write, canonicalize, and verify EVEZ v1 files.

EVEZ files are JSON documents with a stable .evez extension and a SHA-256
integrity envelope. This module deliberately treats payloads as inert data.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

EVEZ_EXTENSION = ".evez"
EVEZ_MEDIA_TYPE = "application/vnd.evez+json"
EVEZ_MAGIC = "EVEZ"
EVEZ_VERSION = 1

STATES = {
    "VERIFIED", "SUPPORTED", "INFERRED", "PROPOSED",
    "UNKNOWN", "STALE", "CONTRADICTED", "RETRACTED",
}


class EVEZFormatError(ValueError):
    """Raised when an EVEZ document violates the v1 format."""


def canonical_bytes(document: dict[str, Any]) -> bytes:
    """Return deterministic bytes used for the v1 SHA-256 digest."""
    copy = json.loads(json.dumps(document))
    integrity = copy.get("integrity")
    if isinstance(integrity, dict):
        integrity.pop("sha256", None)
    return json.dumps(
        copy, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def digest(document: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(document)).hexdigest()


def validate(document: dict[str, Any]) -> None:
    required = {"evez", "version", "kind", "id", "created_at", "state", "payload", "integrity"}
    missing = required - document.keys()
    if missing:
        raise EVEZFormatError(f"missing required fields: {sorted(missing)}")
    if document["evez"] != EVEZ_MAGIC:
        raise EVEZFormatError("invalid EVEZ marker")
    if document["version"] != EVEZ_VERSION:
        raise EVEZFormatError(f"unsupported EVEZ version: {document['version']!r}")
    if not isinstance(document["kind"], str) or not document["kind"]:
        raise EVEZFormatError("kind must be a non-empty string")
    if not isinstance(document["id"], str) or not document["id"]:
        raise EVEZFormatError("id must be a non-empty string")
    if document["state"] not in STATES:
        raise EVEZFormatError(f"invalid epistemic state: {document['state']!r}")
    if not isinstance(document["payload"], dict):
        raise EVEZFormatError("payload must be an object")
    integrity = document["integrity"]
    if not isinstance(integrity, dict) or integrity.get("algorithm") != "sha256":
        raise EVEZFormatError("integrity.algorithm must be sha256")
    stored = integrity.get("sha256")
    if stored is not None and (
        not isinstance(stored, str) or len(stored) != 64 or
        any(c not in "0123456789abcdef" for c in stored)
    ):
        raise EVEZFormatError("integrity.sha256 must be 64 lowercase hex characters or null")


def seal(document: dict[str, Any]) -> dict[str, Any]:
    validate(document)
    document = json.loads(json.dumps(document))
    document.setdefault("integrity", {})["algorithm"] = "sha256"
    document["integrity"]["sha256"] = None
    document["integrity"]["sha256"] = digest(document)
    return document


def verify(document: dict[str, Any]) -> bool:
    validate(document)
    stored = document["integrity"]["sha256"]
    if stored is None:
        return False
    return stored == digest(document)


def loads(text: str, *, verify_integrity: bool = False) -> dict[str, Any]:
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise EVEZFormatError(f"invalid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise EVEZFormatError("EVEZ root must be a JSON object")
    validate(document)
    if verify_integrity and not verify(document):
        raise EVEZFormatError("EVEZ integrity verification failed")
    return document


def dumps(document: dict[str, Any], *, seal_document: bool = True) -> str:
    document = seal(document) if seal_document else document
    validate(document)
    return json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def load(path: str | Path, *, verify_integrity: bool = False) -> dict[str, Any]:
    return loads(Path(path).read_text(encoding="utf-8"), verify_integrity=verify_integrity)


def dump(document: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(dumps(document), encoding="utf-8")
