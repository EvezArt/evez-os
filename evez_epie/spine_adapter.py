"""Local-first adapter between the EPIE ledger and EVEZ-OS Event Spine.

Network writes are explicit. Loopback is the default; remote targets require
an HTTPS URL and an explicit allow_remote=True. The deployed spine must still
be protected by its own access-control boundary.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import math
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

import rfc8785

from .kernel import EVENT_TYPES, EventLedger, canonical_hash

DEFAULT_SPINE_URL = "http://127.0.0.1:9116"
EPIE_ENVELOPE_SCHEMA = "evez.epie.event.v1"


def _base_url(base_url: str, *, allow_remote: bool) -> str:
    if not isinstance(base_url, str) or not base_url:
        raise ValueError("base_url must be a non-empty HTTP(S) URL")
    parsed = urlsplit(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("base_url must use HTTP or HTTPS and include a hostname")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Credentials must not be embedded in base_url")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("base_url must be a service root without path, query, or fragment")
    try:
        loopback = parsed.hostname.lower() == "localhost" or ipaddress.ip_address(parsed.hostname).is_loopback
    except ValueError:
        loopback = parsed.hostname.lower() == "localhost"
    if not loopback and not allow_remote:
        raise PermissionError("Remote spine access requires explicit allow_remote=True")
    if not loopback and parsed.scheme != "https":
        raise PermissionError("Remote spine URLs must use HTTPS")
    return base_url.rstrip("/")


def _request_json(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: Mapping[str, Any] | None = None,
    timeout: float = 3.0,
) -> dict[str, Any]:
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be a positive finite number")
    data = None if payload is None else json.dumps(
        payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    request = Request(
        base_url + path,
        data=data,
        method=method,
        headers={"Accept": "application/json", **({"Content-Type": "application/json"} if data is not None else {})},
    )
    try:
        with urlopen(request, timeout=float(timeout)) as response:
            raw = response.read()
    except HTTPError as exc:
        raise RuntimeError(f"Event Spine returned HTTP {exc.code} for {method} {path}") from exc
    except URLError as exc:
        raise RuntimeError(f"Event Spine request failed for {method} {path}: {exc.reason}") from exc
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Event Spine returned invalid JSON") from exc
    if not isinstance(decoded, dict):
        raise RuntimeError("Event Spine response must be a JSON object")
    return decoded


def _require_capabilities(base_url: str, *, timeout: float) -> dict[str, Any]:
    health = _request_json(base_url, "/health", timeout=timeout)
    if health.get("status") != "alive" or health.get("service") != "event_spine":
        raise RuntimeError("Target is not a healthy EVEZ Event Spine")
    if health.get("event_hash_version") != 2 or health.get("canonicalization") != "RFC8785":
        raise RuntimeError("Target does not advertise RFC 8785 Event Spine v2")
    if health.get("idempotent_append") is not True:
        raise RuntimeError("Target lacks retry-safe idempotent append support")
    return health


def _verify_local_record(event: Mapping[str, Any]) -> None:
    if not isinstance(event, Mapping):
        raise ValueError("EPIE event must be an object")
    sequence = event.get("sequence")
    if type(sequence) is not int or sequence < 0:
        raise ValueError("EPIE event sequence must be a non-negative integer")
    if event.get("event_type") not in EVENT_TYPES:
        raise ValueError("EPIE event type is not in the existing event vocabulary")
    digest = event.get("event_hash")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("EPIE event hash is malformed")
    expected = canonical_hash({key: value for key, value in event.items() if key != "event_hash"})
    if digest != expected:
        raise ValueError("EPIE event content hash mismatch")


def _verify_remote_record(event: Mapping[str, Any]) -> None:
    if not isinstance(event, Mapping):
        raise ValueError("Remote spine event must be an object")
    digest = event.get("hash")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("Remote spine hash is malformed")
    version = event.get("hash_version", 1)
    if type(version) is not int:
        raise ValueError("Remote hash version must be an integer")
    if version == 2:
        expected = hashlib.sha256(
            rfc8785.dumps({key: value for key, value in event.items() if key != "hash"})
        ).hexdigest()
    elif version == 1:
        hash_input = (
            f"{event['seq']}:{event['prev_hash']}:{event['domain']}:"
            f"{event['action']}:{json.dumps(event['data'], sort_keys=True, default=str)}"
        )
        expected = hashlib.sha256(hash_input.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported remote hash version: {version}")
    if digest != expected:
        raise ValueError("Remote spine event content hash mismatch")


def _append_validated(
    base_url: str,
    event: Mapping[str, Any],
    *,
    timeout: float,
) -> dict[str, Any]:
    _verify_local_record(event)
    envelope = {"schema": EPIE_ENVELOPE_SCHEMA, "event": dict(event)}
    remote = _request_json(
        base_url,
        "/append",
        method="POST",
        payload={
            "domain": "epie",
            "action": event["event_type"],
            "data": envelope,
            "idempotency_key": event["event_hash"],
        },
        timeout=timeout,
    )
    _verify_remote_record(remote)
    if remote.get("domain") != "epie" or remote.get("action") != event["event_type"]:
        raise RuntimeError("Spine response does not identify the committed EPIE event")
    if remote.get("idempotency_key") != event["event_hash"]:
        raise RuntimeError("Spine response did not confirm the EPIE idempotency key")
    returned = remote.get("data")
    if not isinstance(returned, Mapping) or returned.get("schema") != EPIE_ENVELOPE_SCHEMA:
        raise RuntimeError("Spine response is missing the EPIE envelope")
    if not isinstance(returned.get("event"), Mapping) or returned["event"].get("event_hash") != event["event_hash"]:
        raise RuntimeError("Spine response does not contain the committed EPIE record")
    return {
        "sequence": remote["seq"],
        "spine_hash": remote["hash"],
        "epie_event_hash": event["event_hash"],
        "idempotency_key": remote["idempotency_key"],
    }


def append_to_spine(
    event: Mapping[str, Any],
    *,
    base_url: str = DEFAULT_SPINE_URL,
    allow_remote: bool = False,
    timeout: float = 3.0,
) -> dict[str, Any]:
    """Append one committed EPIE event with a retry-safe idempotency key."""
    base = _base_url(base_url, allow_remote=allow_remote)
    _require_capabilities(base, timeout=timeout)
    return _append_validated(base, event, timeout=timeout)


def verify_spine(
    *,
    base_url: str = DEFAULT_SPINE_URL,
    domain: str = "epie",
    allow_remote: bool = False,
    timeout: float = 3.0,
) -> dict[str, Any]:
    """Verify global spine status, projected record hashes, and the embedded EPIE chain."""
    if not isinstance(domain, str) or not domain or "/" in domain:
        raise ValueError("domain must be a non-empty single path segment")
    base = _base_url(base_url, allow_remote=allow_remote)
    _require_capabilities(base, timeout=timeout)
    remote_verify = _request_json(base, "/verify", timeout=timeout)
    projection = _request_json(base, "/project/" + quote(domain, safe=""), timeout=timeout)
    remote_events = projection.get("events")
    if not isinstance(remote_events, list):
        raise RuntimeError("Spine projection omitted its events array")

    errors = []
    warnings = list(remote_verify.get("warnings", [])) if isinstance(remote_verify.get("warnings"), list) else []
    epie_events = []
    previous_seq = -1
    for index, remote_event in enumerate(remote_events):
        try:
            _verify_remote_record(remote_event)
            seq = remote_event.get("seq")
            if type(seq) is not int or seq <= previous_seq:
                raise ValueError("Projected global sequence is not strictly increasing")
            previous_seq = seq
            data = remote_event.get("data")
            if isinstance(data, Mapping) and data.get("schema") == EPIE_ENVELOPE_SCHEMA:
                inner = data.get("event")
                _verify_local_record(inner)
                epie_events.append(dict(inner))
        except Exception as exc:
            errors.append({"index": index, "error": str(exc)})

    local_chain = {"valid": True, "reason": "no embedded EPIE events"}
    if epie_events:
        try:
            ledger = EventLedger(epie_events)
            local_chain = {"valid": True, "reason": "ok", "event_count": len(epie_events),
                           "head_hash": ledger.replay()["head_hash"]}
        except Exception as exc:
            local_chain = {"valid": False, "reason": str(exc)}
            errors.append({"index": "epie-chain", "error": str(exc)})

    global_valid = remote_verify.get("valid") is True
    if not global_valid:
        errors.append({"index": "global-chain", "error": "Event Spine's full-chain verification failed"})
    valid = global_valid and not errors and local_chain["valid"]
    return {
        "valid": valid,
        "global_chain_valid": global_valid,
        "projected_events": len(remote_events),
        "embedded_epie_events": len(epie_events),
        "epie_chain": local_chain,
        "errors": errors,
        "warnings": warnings,
    }


def sync_ledger_to_spine(
    ledger: EventLedger,
    *,
    base_url: str = DEFAULT_SPINE_URL,
    allow_remote: bool = False,
    timeout: float = 3.0,
) -> dict[str, Any]:
    """Synchronize a complete valid local ledger; retries are idempotent.

    The existing embedded EPIE records must form a prefix of the local chain.
    A gap or different head stops synchronization rather than silently forking.
    """
    if not isinstance(ledger, EventLedger):
        raise TypeError("ledger must be an EventLedger")
    valid, reason = ledger.verify()
    if not valid:
        raise ValueError(f"Local EPIE ledger is invalid: {reason}")
    local_events = ledger.events
    base = _base_url(base_url, allow_remote=allow_remote)
    _require_capabilities(base, timeout=timeout)
    before = verify_spine(base_url=base, domain="epie", allow_remote=allow_remote, timeout=timeout)
    if not before["valid"]:
        raise RuntimeError("Refusing to sync into an invalid Event Spine")

    projection = _request_json(base, "/project/epie", timeout=timeout)
    remote_epie = []
    for remote in projection.get("events", []):
        data = remote.get("data")
        if isinstance(data, Mapping) and data.get("schema") == EPIE_ENVELOPE_SCHEMA:
            remote_epie.append(data["event"])
    if len(remote_epie) > len(local_events):
        raise RuntimeError("Remote EPIE chain is longer than the local source ledger")
    for index, remote_event in enumerate(remote_epie):
        if remote_event.get("event_hash") != local_events[index].get("event_hash"):
            raise RuntimeError("Remote EPIE events are not a prefix of the local source ledger")

    appended = []
    skipped = len(remote_epie)
    for event in local_events[len(remote_epie):]:
        appended.append(_append_validated(base, event, timeout=timeout))

    after = verify_spine(base_url=base, domain="epie", allow_remote=allow_remote, timeout=timeout)
    if not after["valid"]:
        raise RuntimeError("Post-sync verification failed")
    return {
        "valid": True,
        "appended_count": len(appended),
        "already_present_count": skipped,
        "appended": appended,
        "verification": after,
    }
