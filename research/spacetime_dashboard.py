#!/usr/bin/env python3
"""Loopback-only, read-only EVEZ spacetime research dashboard (standard library)."""
from __future__ import annotations
import argparse
import ipaddress
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from typing import Any

from research.spacetime_breakthrough_lab import experiment_summary, DEFAULT_LEDGER
from research.spacetime_interval import classify_interval
from research.warp_bubble_profile import analyze_profile

MAX_REQUEST_TARGET = 8192
MAX_QUERY_FIELDS = 8
MAX_PROFILE_SAMPLES = 2001
HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark light"><title>EVEZ Spacetime Lab</title>
<style>
:root{font-family:system-ui,sans-serif;color-scheme:dark light}body{max-width:940px;margin:0 auto;padding:1rem;line-height:1.5}
header{border-bottom:1px solid #8885;margin-bottom:1rem}h1{font-size:1.6rem}section{border:1px solid #8885;border-radius:12px;padding:1rem;margin:1rem 0}
label{display:block;margin:.6rem 0}input{padding:.55rem;max-width:14rem;width:95%}button{padding:.6rem 1rem;cursor:pointer}
pre{padding:.7rem;background:#8882;border-radius:8px;white-space:pre-wrap;overflow-wrap:anywhere}.muted{opacity:.8}
</style></head><body>
<header><h1>EVEZ Spacetime Research Lab</h1><p class="muted">Local-first · read-only dashboard · no claim of propulsion feasibility</p></header>
<section><h2>Evidence ledger</h2><button id="refresh">Verify / refresh summary</button><pre id="ledger">Loading…</pre></section>
<section><h2>Spacetime interval</h2><p>Flat Minkowski signature (+,−): s² = c²Δt² − Δx². A spacelike classification is not FTL communication.</p>
<label>Δt seconds <input id="dt" type="number" step="any" value="1e-9"></label>
<label>Δx meters <input id="dx" type="number" step="any" value="1"></label><button id="interval">Classify interval</button><pre id="interval-result">Not run</pre></section>
<section><h2>Bubble shape ansatz</h2><p>This samples only a shape function and its derivative. It does not solve Einstein's equations or calculate stress-energy.</p>
<label>Radius (meters) <input id="radius" type="number" min="0.001" step="any" value="10"></label>
<label>Wall steepness (1/meters) <input id="sigma" type="number" min="0.000001" step="any" value="1"></label>
<label>Samples (11–2001) <input id="samples" type="number" min="11" max="2001" step="1" value="401"></label>
<button id="profile">Analyze profile</button><pre id="profile-result">Not run</pre></section>
<script>
async function getJSON(path){const r=await fetch(path,{cache:"no-store"});const d=await r.json();if(!r.ok)throw new Error(d.error||("HTTP "+r.status));return d}
async function show(id,fn){const target=document.getElementById(id);target.textContent="Running…";try{target.textContent=JSON.stringify(await fn(),null,2)}catch(e){target.textContent="Error: "+e.message}}
document.getElementById("refresh").onclick=()=>show("ledger",()=>getJSON("/api/report"));
document.getElementById("interval").onclick=()=>show("interval-result",()=>getJSON("/api/interval?dt="+encodeURIComponent(document.getElementById("dt").value)+"&dx="+encodeURIComponent(document.getElementById("dx").value)));
document.getElementById("profile").onclick=()=>show("profile-result",()=>getJSON("/api/profile?radius="+encodeURIComponent(document.getElementById("radius").value)+"&sigma="+encodeURIComponent(document.getElementById("sigma").value)+"&samples="+encodeURIComponent(document.getElementById("samples").value)));
document.getElementById("refresh").click();document.getElementById("interval").click();document.getElementById("profile").click();
</script></body></html>"""


def json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def create_handler(ledger_path: str | Path):
    ledger = Path(ledger_path).expanduser()

    class Handler(BaseHTTPRequestHandler):
        server_version = "EVEZ-Spacetime-Dashboard/1.0"
        sys_version = ""

        def log_message(self, format: str, *args: Any) -> None:
            # Do not print request paths or query values into shared terminal logs.
            return

        def _send(self, status: int, data: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(data)

        def _json(self, status: int, data: Any) -> None:
            self._send(status, json_bytes(data), "application/json; charset=utf-8")

        def do_GET(self) -> None:
            if len(self.path) > MAX_REQUEST_TARGET:
                self._json(414, {"ok": False, "error": "request target too long"})
                return
            parsed = urlsplit(self.path)
            try:
                query = parse_qs(parsed.query, keep_blank_values=False, strict_parsing=False, max_num_fields=MAX_QUERY_FIELDS)
                if parsed.path == "/":
                    self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
                    return
                if parsed.path == "/api/health":
                    self._json(200, {"ok": True, "service": "evez-spacetime-dashboard", "mode": "read-only", "bind_scope": "loopback"})
                    return
                if parsed.path == "/api/report":
                    report = experiment_summary(ledger)
                    experiment = report.get("experiment")
                    self._json(200, {
                        "verification": report["verification"],
                        "experiment": None if experiment is None else {
                            "experiment_id": experiment["experiment_id"],
                            "title": experiment["title"],
                            "claim_classification": experiment["claim_classification"],
                            "epistemic_status": experiment["epistemic_status"],
                        },
                        "observations_count": len(report.get("observations") or []),
                        "analysis_notes_count": len(report.get("notes") or []),
                        "privacy_note": "Only summary counts and experiment metadata are returned; observation details and notes are not exposed by this dashboard."
                    })
                    return
                if parsed.path == "/api/interval":
                    dt = _one_float(query, "dt")
                    dx = _one_float(query, "dx")
                    self._json(200, classify_interval(dt, dx))
                    return
                if parsed.path == "/api/profile":
                    radius = _one_float(query, "radius")
                    sigma = _one_float(query, "sigma")
                    samples = _one_int(query, "samples", 401)
                    if samples > MAX_PROFILE_SAMPLES:
                        raise ValueError(f"samples must not exceed {MAX_PROFILE_SAMPLES} in dashboard mode")
                    profile = analyze_profile(radius, sigma, samples)
                    profile.pop("profile", None)
                    self._json(200, profile)
                    return
                self._json(404, {"ok": False, "error": "not found"})
            except (ValueError, TypeError, OverflowError) as exc:
                self._json(400, {"ok": False, "error": str(exc)})

        def do_POST(self) -> None:
            self._json(405, {"ok": False, "error": "read-only service"})
        do_PUT = do_POST
        do_PATCH = do_POST
        do_DELETE = do_POST

    return Handler


def _one_float(query: dict[str, list[str]], key: str) -> float:
    values = query.get(key, [])
    if len(values) != 1 or not values[0]:
        raise ValueError(f"exactly one {key} value is required")
    try:
        value = float(values[0])
    except ValueError:
        raise ValueError(f"{key} must be numeric") from None
    if not __import__("math").isfinite(value):
        raise ValueError(f"{key} must be finite")
    return value


def _one_int(query: dict[str, list[str]], key: str, default: int) -> int:
    values = query.get(key, [])
    if not values:
        return default
    if len(values) != 1:
        raise ValueError(f"exactly one {key} value is allowed")
    try:
        value = int(values[0])
    except ValueError:
        raise ValueError(f"{key} must be an integer") from None
    if value < 11:
        raise ValueError(f"{key} must be at least 11")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=Path(os.environ.get("EVEZ_SPACETIME_LEDGER", str(DEFAULT_LEDGER))))
    parser.add_argument("--host", default="127.0.0.1", help="must be a loopback IP address; dashboard is not authenticated")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args(argv)
    try:
        host_ip = ipaddress.ip_address(args.host)
        if not host_ip.is_loopback:
            raise ValueError("--host must be a loopback IP address (127.0.0.1 or ::1)")
        if not 1 <= args.port <= 65535:
            raise ValueError("port must be in [1, 65535]")
        server = ThreadingHTTPServer((args.host, args.port), create_handler(args.ledger))
    except (ValueError, OSError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, separators=(",", ":")), file=sys.stderr)
        return 2
    print(f"EVEZ spacetime dashboard listening on http://{args.host}:{args.port}; read-only; no authentication; loopback only", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
