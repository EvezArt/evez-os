#!/usr/bin/env python3
"""Read-only, secret-safe inventory for the EVEZ mobile operator.

This command inventories local executable availability and performs one
unauthenticated HTTP GET to the configured EVEZ health endpoint. It does not
start processes, invoke agents, source shell configuration, or expose secrets.
"""
from __future__ import annotations

import json
import os
import shutil
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def configured_endpoint() -> str:
    """Read only EVEZ_ENDPOINT from the config file without sourcing it."""
    config_path = Path(os.environ.get(
        "EVEZ_CONFIG", str(Path.home() / ".config/evez/evez.env")
    ))
    try:
        lines = config_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return os.environ.get("EVEZ_ENDPOINT", "https://evez-os.ai")

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[7:].lstrip()
        if not stripped.startswith("EVEZ_ENDPOINT="):
            continue
        value = stripped.split("=", 1)[1].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if value and "$(" not in value and "`" not in value:
            return value
    return os.environ.get("EVEZ_ENDPOINT", "https://evez-os.ai")


def probe_health(endpoint: str) -> dict:
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return {"status": "NOT_TESTED", "reason": "invalid_endpoint_scheme_or_host"}
    url = endpoint.rstrip("/") + "/health"
    request = urllib.request.Request(url, headers={"Accept": "application/json"},
                                     method="GET")
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return {"status": "REACHABLE" if 200 <= response.status < 300 else "UNHEALTHY",
                    "http_status": response.status}
    except urllib.error.HTTPError as exc:
        return {"status": "UNHEALTHY", "http_status": exc.code}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        # Return only the exception class; avoid leaking URLs or environment data.
        return {"status": "UNREACHABLE", "reason": type(exc).__name__}


def main() -> int:
    commands = ("evezctl", "hermes", "openclaw", "git", "python")
    available = {name: shutil.which(name) is not None for name in commands}
    endpoint = configured_endpoint()
    parsed = urllib.parse.urlparse(endpoint)
    # Report only the origin, never credentials, query strings, or fragments.
    safe_origin = (f"{parsed.scheme}://{parsed.netloc}"
                   if parsed.scheme in ("http", "https") and parsed.netloc
                   else "INVALID_ENDPOINT")
    result = {
        "schema_version": 1,
        "mode": "read_only",
        "local_commands_available": available,
        "config_files_present": {
            "evez_config": Path(os.environ.get(
                "EVEZ_CONFIG", str(Path.home() / ".config/evez/evez.env")
            )).is_file(),
            "hermes_config": (Path.home() / ".hermes").exists(),
            "openclaw_config": (Path.home() / ".openclaw").exists(),
        },
        "evez_gateway": {
            "origin": safe_origin,
            "health": probe_health(endpoint),
        },
        "limitations": [
            "Command availability does not prove a service is running.",
            "Configuration presence does not prove authentication or connectivity.",
            "Hermes and OpenClaw APIs are not invoked by this inventory.",
            "Only the unauthenticated GET /health probe is attempted.",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
