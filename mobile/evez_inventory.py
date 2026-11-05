#!/usr/bin/env python3
"""Read-only, secret-safe inventory for the EVEZ mobile operator.

This command inventories local executable availability and performs at most one
unauthenticated HTTP GET to an explicitly configured EVEZ health endpoint. It
does not start processes, invoke agents, source shell configuration, or expose
secrets. If no endpoint is configured, no network request is made.
"""
from __future__ import annotations

import json
import os
import shutil
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def configured_endpoint() -> str | None:
    """Read EVEZ_ENDPOINT without sourcing or executing the config file."""
    env_endpoint = os.environ.get("EVEZ_ENDPOINT", "").strip()
    if env_endpoint:
        return env_endpoint

    config_path = Path(os.environ.get(
        "EVEZ_CONFIG", str(Path.home() / ".config/evez/evez.env")
    ))
    try:
        lines = config_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None

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
    return None


def probe_health(endpoint: str | None) -> dict:
    if not endpoint:
        return {"status": "NOT_CONFIGURED"}
    parsed = urllib.parse.urlparse(endpoint)
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        return {
            "status": "NOT_TESTED",
            "reason": "endpoint_must_be_http_origin_without_credentials_query_or_fragment",
        }

    # Build the request from the parsed host, not untrusted URL credentials
    # or query fragments. Preserve an optional base path for reverse proxies.
    host = parsed.hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    try:
        port = f":{parsed.port}" if parsed.port is not None else ""
    except ValueError:
        return {"status": "NOT_TESTED", "reason": "invalid_endpoint_port"}
    base_path = parsed.path.rstrip("/")
    url = f"{parsed.scheme}://{host}{port}{base_path}/health"
    request = urllib.request.Request(
        url, headers={"Accept": "application/json"}, method="GET"
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return {
                "status": "REACHABLE" if 200 <= response.status < 300 else "UNHEALTHY",
                "http_status": response.status,
            }
    except urllib.error.HTTPError as exc:
        return {"status": "UNHEALTHY", "http_status": exc.code}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        # Return only the exception class; avoid leaking URLs or environment data.
        return {"status": "UNREACHABLE", "reason": type(exc).__name__}


def safe_origin(endpoint: str | None) -> str:
    if not endpoint:
        return "NOT_CONFIGURED"
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return "INVALID_ENDPOINT"
    try:
        port = f":{parsed.port}" if parsed.port is not None else ""
    except ValueError:
        return "INVALID_ENDPOINT"
    host = parsed.hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    # Never display credentials, query strings, or fragments.
    return f"{parsed.scheme}://{host}{port}"


def main() -> int:
    commands = ("evezctl", "hermes", "openclaw", "git", "python")
    available = {name: shutil.which(name) is not None for name in commands}
    config_path = Path(os.environ.get(
        "EVEZ_CONFIG", str(Path.home() / ".config/evez/evez.env")
    ))
    endpoint = configured_endpoint()
    result = {
        "schema_version": 1,
        "mode": "read_only",
        "local_commands_available": available,
        "config_files_present": {
            "evez_config": config_path.is_file(),
            "hermes_config": (Path.home() / ".hermes").exists(),
            "openclaw_config": (Path.home() / ".openclaw").exists(),
        },
        "evez_gateway": {
            "origin": safe_origin(endpoint),
            "health": probe_health(endpoint),
        },
        "limitations": [
            "Command availability does not prove a service is running.",
            "Configuration presence does not prove authentication or connectivity.",
            "Hermes and OpenClaw APIs are not invoked by this inventory.",
            "No network request is made unless EVEZ_ENDPOINT is explicitly configured.",
            "The only permitted network operation is an unauthenticated GET /health with a three-second timeout.",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
