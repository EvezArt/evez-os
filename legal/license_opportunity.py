#!/usr/bin/env python3
"""Audit declared rights and identify licensing opportunities without inventing ownership."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


LICENSE_PATTERNS = {
    "MIT": re.compile(r"\bMIT License\b|\bSPDX-License-Identifier:\s*MIT\b", re.I),
    "Apache-2.0": re.compile(r"\bApache(?: License)?(?:,| version)?\s*2\.0\b|\bApache-2\.0\b", re.I),
    "BSD": re.compile(r"\bBSD(?:-|\s+)[123]\b|\bBSD License\b", re.I),
    "GPL": re.compile(r"\bGNU General Public License\b|\bGPL-[23](?:\.[01])?(?:-or-later|-only)?\b", re.I),
    "LGPL": re.compile(r"\bGNU Lesser General Public License\b|\bLGPL-[23]\b", re.I),
    "MPL-2.0": re.compile(r"\bMozilla Public License(?:,| version)?\s*2\.0\b|\bMPL-2\.0\b", re.I),
    "CC-BY-4.0": re.compile(r"\bCC-BY-4\.0\b|\bCreative Commons Attribution 4\.0\b", re.I),
    "CC-BY-NC-4.0": re.compile(r"\bCC-BY-NC-4\.0\b", re.I),
    "MIT-0": re.compile(r"\bMIT-0\b", re.I),
}

ASSET_CLASSES = {
    ".py": "SOURCE_CODE",
    ".js": "SOURCE_CODE",
    ".ts": "SOURCE_CODE",
    ".tsx": "SOURCE_CODE",
    ".jsx": "SOURCE_CODE",
    ".rs": "SOURCE_CODE",
    ".go": "SOURCE_CODE",
    ".sh": "SOURCE_CODE",
    ".md": "DOCUMENTATION",
    ".txt": "TEXT",
    ".json": "DATA_OR_CONFIG",
    ".yaml": "DATA_OR_CONFIG",
    ".yml": "DATA_OR_CONFIG",
    ".png": "MEDIA",
    ".jpg": "MEDIA",
    ".jpeg": "MEDIA",
    ".webp": "MEDIA",
    ".mp3": "MEDIA",
    ".wav": "MEDIA",
    ".mp4": "MEDIA",
}


@dataclass(frozen=True)
class RightsFinding:
    path: str
    asset_class: str
    declared_licenses: tuple[str, ...]
    status: str
    monetization_paths: tuple[str, ...]
    legal_review: bool
    reason: str


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def detect_license(text: str) -> list[str]:
    return sorted(name for name, pattern in LICENSE_PATTERNS.items() if pattern.search(text))


def classify(path: Path) -> str:
    return ASSET_CLASSES.get(path.suffix.lower(), "OTHER")


def monetization_paths(asset_class: str, licenses: list[str]) -> tuple[str, ...]:
    if asset_class == "SOURCE_CODE":
        if any(name in licenses for name in ("MIT", "MIT-0", "Apache-2.0", "BSD")):
            return ("hosted_service", "support", "enterprise_integration", "training")
        return ("rights_review", "commercial_license_candidate")
    if asset_class == "DOCUMENTATION":
        return ("training", "documentation_subscription", "commercial_support")
    if asset_class == "MEDIA":
        return ("media_license", "syndication", "brand_license")
    if asset_class == "DATA_OR_CONFIG":
        return ("data_license_review", "hosted_service")
    if asset_class == "TEXT":
        return ("publication", "training")
    return ("commercial_review",)


def audit(root: Path) -> dict[str, Any]:
    findings: list[RightsFinding] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in {".git", ".venv", "node_modules", "__pycache__"} for part in path.parts):
            continue

        asset_class = classify(path)
        if asset_class == "OTHER":
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        declared = detect_license(text)
        if path.name.upper().startswith("LICENSE"):
            status = "LICENSE_DOCUMENT"
            reason = "license document detected"
        elif declared:
            status = "DECLARED"
            reason = "license expression or license language detected in asset"
        else:
            status = "UNDECLARED"
            reason = "no recognized license declaration found; do not assume rights"

        legal_review = status != "DECLARED" or "CC-BY-NC-4.0" in declared
        findings.append(
            RightsFinding(
                path=str(path.relative_to(root)),
                asset_class=asset_class,
                declared_licenses=tuple(declared),
                status=status,
                monetization_paths=monetization_paths(asset_class, declared),
                legal_review=legal_review,
                reason=reason,
            )
        )

    result = {
        "schema": "evez-license-opportunity-v1",
        "rights_model": "OWNERSHIP_FIRST",
        "findings": [asdict(row) for row in findings],
        "summary": {
            "assets": len(findings),
            "declared": sum(row.status == "DECLARED" for row in findings),
            "undeclared": sum(row.status == "UNDECLARED" for row in findings),
            "legal_review": sum(row.legal_review for row in findings),
        },
        "opportunity_classes": [
            "hosted_service",
            "support",
            "enterprise_integration",
            "commercial_license_candidate",
            "media_license",
            "syndication",
            "brand_license",
            "training",
            "documentation_subscription",
            "publication",
            "data_license_review",
        ],
    }
    result["audit_sha256"] = digest(result)
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.root), indent=2, sort_keys=True))
