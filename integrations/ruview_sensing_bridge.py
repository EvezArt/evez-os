#!/usr/bin/env python3
"""Optional RuView WebSocket-to-witness-ledger adapter.

Captures only scalar RF environment summaries. Never stores raw CSI arrays,
node identifiers, person/presence labels, or vital-sign fields. Requires the
optional websockets package; the offline core remains standard-library-only.
"""
from __future__ import annotations
import argparse
import asyncio
import ipaddress
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from research import spacetime_breakthrough_lab as lab  # noqa: E402

ALLOWED_FEATURES = {"mean_rssi": "dBm", "variance": "source_native", "motion_band_power": "source_native"}
MAX_FRAME_BYTES = 1_048_576


def validate_ws_url(url: str, *, token_present: bool, allow_remote_wss: bool = False) -> str:
    if not isinstance(url, str) or not url.strip():
        raise ValueError("RUVIEW_WS_URL must be set to a WebSocket URL")
    parsed = urlsplit(url.strip())
    if parsed.scheme not in {"ws", "wss"} or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ValueError("RuView endpoint must be a ws:// or wss:// URL without embedded credentials or fragments")
    host = parsed.hostname.lower().rstrip(".")
    is_loopback = host == "localhost" or host.endswith(".localhost")
    try:
        is_loopback = is_loopback or ipaddress.ip_address(host).is_loopback
    except ValueError:
        pass
    if parsed.scheme == "ws" and not is_loopback:
        raise ValueError("unencrypted ws:// is allowed only for localhost; use wss:// for remote sensing")
    if not is_loopback:
        if parsed.scheme != "wss":
            raise ValueError("remote RuView endpoints must use wss://")
        if not host.endswith(".ts.net") and not allow_remote_wss:
            raise ValueError("remote WSS hosts must be in the tailnet .ts.net domain unless RUVIEW_ALLOW_REMOTE_WSS=1")
        if not token_present:
            raise ValueError("RUVIEW_API_TOKEN is required for non-loopback sensing endpoints")
    return url.strip()


def _timestamp_from_frame(frame: dict[str, Any], received_at: str | None = None) -> str:
    raw = frame.get("timestamp")
    if isinstance(raw, (int, float)) and not isinstance(raw, bool) and math.isfinite(float(raw)):
        # Accept plausible UNIX seconds or milliseconds; ignore tick counters.
        seconds = float(raw) / 1000.0 if float(raw) > 100_000_000_000 else float(raw)
        if 946684800 <= seconds <= 4_102_444_800:
            return datetime.fromtimestamp(seconds, timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    if isinstance(raw, str):
        try:
            value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        except ValueError:
            pass
    return received_at or lab.utc_now()


def extract_observations(frame: Any, *, calibration_id: str, received_at: str | None = None) -> list[dict[str, Any]]:
    if not isinstance(frame, dict):
        return []
    if not isinstance(calibration_id, str) or not calibration_id.strip():
        raise ValueError("a documented RUVIEW_CALIBRATION_ID is required")
    features = frame.get("features")
    if not isinstance(features, dict):
        return []
    reported_source = frame.get("source")
    source_mode = reported_source if reported_source in {"live", "simulated"} else "unknown"
    observed_at = _timestamp_from_frame(frame, received_at)
    observations = []
    for name, unit in ALLOWED_FEATURES.items():
        value = features.get(name)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            continue
        observations.append({
            "source": f"ruview:{source_mode}",
            "modality": "ruview_csi",
            "quantity": f"features.{name}",
            "value": value,
            "unit": unit,
            "uncertainty": None,
            "calibration_id": calibration_id.strip(),
            "evidence_uri": None,
            "evidence_sha256": None,
            "notes": "Scalar RF-environment summary only; raw CSI, node IDs, presence/person labels, and vital-sign fields intentionally omitted.",
            "observed_at": observed_at,
        })
    return observations


async def run_stream(url: str, ledger_path: Path, calibration_id: str, every_seconds: float, token: str | None) -> None:
    try:
        from websockets.asyncio.client import connect
    except ImportError:
        raise RuntimeError("optional dependency missing; install requirements-ruview-bridge.txt") from None
    headers = {"Authorization": f"Bearer {token}"} if token else None
    last_sample = 0.0
    while True:
        try:
            async with connect(url, additional_headers=headers, max_size=MAX_FRAME_BYTES,
                               open_timeout=10, close_timeout=5, ping_interval=20, ping_timeout=20) as websocket:
                print("Connected to RuView sensing stream; only scalar RF features will be recorded.", flush=True)
                async for payload in websocket:
                    now = time.monotonic()
                    if now - last_sample < every_seconds:
                        continue
                    last_sample = now
                    if not isinstance(payload, str) or len(payload.encode("utf-8", errors="ignore")) > MAX_FRAME_BYTES:
                        continue
                    try:
                        frame = json.loads(payload)
                    except json.JSONDecodeError:
                        continue
                    observations = extract_observations(frame, calibration_id=calibration_id)
                    for observation in observations:
                        result = lab.append_event(ledger_path, {
                            "event_type": "SPACETIME_LAB.OBSERVATION_RECORDED",
                            "observation": observation,
                        })
                        print(json.dumps({"ok": True, "sequence": result["sequence"],
                                          "quantity": observation["quantity"],
                                          "event_hash_prefix": result["event_hash"][:12]}, separators=(",", ":")), flush=True)
        except asyncio.CancelledError:
            raise
        except Exception:
            print("RuView connection failed or closed; retrying in 5s. Endpoint, token, and payload details are withheld.", file=sys.stderr, flush=True)
            await asyncio.sleep(5)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=Path(os.environ.get("EVEZ_SPACETIME_LEDGER", str(lab.DEFAULT_LEDGER))))
    parser.add_argument("--every-seconds", type=float, default=5.0)
    args = parser.parse_args(argv)
    url = os.environ.get("RUVIEW_WS_URL", "").strip()
    token = os.environ.get("RUVIEW_API_TOKEN", "").strip() or None
    calibration_id = os.environ.get("RUVIEW_CALIBRATION_ID", "").strip()
    try:
        allow_remote = os.environ.get("RUVIEW_ALLOW_REMOTE_WSS", "") == "1"
        url = validate_ws_url(url, token_present=token is not None, allow_remote_wss=allow_remote)
        if not calibration_id:
            raise ValueError("RUVIEW_CALIBRATION_ID must identify the calibration/protocol version")
        if not math.isfinite(args.every_seconds) or args.every_seconds < 0.5 or args.every_seconds > 3600:
            raise ValueError("--every-seconds must be between 0.5 and 3600")
        report = lab.experiment_summary(args.ledger)
        if not report["verification"]["ok"]:
            raise ValueError("ledger integrity check failed; refusing sensor ingest")
        if report["experiment"] is None:
            raise ValueError("register an experiment before starting RuView ingest")
        asyncio.run(run_stream(url, args.ledger, calibration_id, args.every_seconds, token))
        return 0
    except KeyboardInterrupt:
        print("RuView sensing bridge stopped.", flush=True)
        return 0
    except (ValueError, OSError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, separators=(",", ":")), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
