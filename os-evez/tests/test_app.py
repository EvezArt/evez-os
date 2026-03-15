"""Tests for opengarden.app.main — FastAPI HTTP endpoints."""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Create a TestClient with an isolated data directory."""
    monkeypatch.setenv("OG_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("OG_CREATOR_NAME", "Test Creator")
    monkeypatch.setenv("OG_CREATOR_HANDLE", "TESTHANDLE")
    monkeypatch.setenv("OG_CREATOR_REPO", "github.com/test/repo")
    monkeypatch.setenv("OG_LICENSE_ID", "MIT")
    monkeypatch.setenv("OG_DOWNLOAD_TOKEN", "")
    monkeypatch.setenv("OG_FREE_LAG_RUNS", "2")

    # Re-import app so env vars are picked up
    if "opengarden.app.main" in sys.modules:
        del sys.modules["opengarden.app.main"]

    from opengarden.app.main import app
    return TestClient(app, raise_server_exceptions=True)


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

def test_health_returns_ok(client):
    """/health endpoint returns ok=True."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True


def test_health_returns_creator_fields(client):
    """/health includes creator, handle, repo, and ts."""
    resp = client.get("/health")
    data = resp.json()
    assert "creator" in data
    assert "handle" in data
    assert "repo" in data
    assert "ts" in data


# ---------------------------------------------------------------------------
# /arcade
# ---------------------------------------------------------------------------

def test_arcade_returns_html(client):
    """/arcade returns HTML content."""
    resp = client.get("/arcade")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "OS-EVEZ ARCADE" in resp.text


def test_arcade_shows_no_runs_message_when_empty(client):
    """/arcade shows placeholder when no runs exist."""
    resp = client.get("/arcade")
    assert "No runs yet" in resp.text


# ---------------------------------------------------------------------------
# /runs/create  →  /runs/{run_id}  →  /latest
# ---------------------------------------------------------------------------

def test_create_run_returns_run_id(client):
    """POST /runs/create creates a run and returns its ID."""
    resp = client.post("/runs/create", json={"seed": 1, "steps": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert "run_id" in data
    assert data["steps"] == 5


def test_create_run_returns_root_hash(client):
    """POST /runs/create response contains a non-empty root_hash."""
    resp = client.post("/runs/create", json={"seed": 7, "steps": 3})
    data = resp.json()
    assert len(data["root_hash"]) == 64  # sha256 hex


def test_create_run_creates_run_directory(client, tmp_path):
    """POST /runs/create actually creates the run directory on disk."""
    resp = client.post("/runs/create", json={"seed": 42, "steps": 5})
    run_id = resp.json()["run_id"]
    run_dir = tmp_path / "runs" / run_id
    assert run_dir.exists()
    assert (run_dir / "spine.jsonl").exists()
    assert (run_dir / "manifest.json").exists()


def test_get_run_after_create(client):
    """GET /runs/{run_id} returns run info after creation."""
    create_resp = client.post("/runs/create", json={"seed": 10, "steps": 4})
    run_id = create_resp.json()["run_id"]
    resp = client.get(f"/runs/{run_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["run_id"] == run_id
    assert "root_hash" in data
    assert isinstance(data["files"], list)


def test_get_run_not_found(client):
    """GET /runs/{run_id} returns 404 for a non-existent run."""
    resp = client.get("/runs/does_not_exist_99999")
    assert resp.status_code == 404


def test_latest_returns_404_when_no_runs(client):
    """GET /latest returns 404 when no runs have been created."""
    resp = client.get("/latest")
    assert resp.status_code == 404


def test_latest_returns_most_recent_run(client):
    """GET /latest returns the most recently created run."""
    client.post("/runs/create", json={"seed": 1, "steps": 3})
    resp2 = client.post("/runs/create", json={"seed": 2, "steps": 3})
    latest_run_id = resp2.json()["run_id"]
    resp = client.get("/latest")
    assert resp.status_code == 200
    data = resp.json()
    assert data["run_id"] == latest_run_id


# ---------------------------------------------------------------------------
# /latest/download  and  /runs/{run_id}/download
# ---------------------------------------------------------------------------

def test_latest_download_no_token_required_when_token_empty(client):
    """GET /latest/download succeeds when OG_DOWNLOAD_TOKEN is empty."""
    client.post("/runs/create", json={"seed": 5, "steps": 3})
    resp = client.get("/latest/download")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"


def test_run_download_returns_zip(client):
    """GET /runs/{run_id}/download returns a zip file."""
    create_resp = client.post("/runs/create", json={"seed": 3, "steps": 3})
    run_id = create_resp.json()["run_id"]
    resp = client.get(f"/runs/{run_id}/download")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"


# ---------------------------------------------------------------------------
# /free/download
# ---------------------------------------------------------------------------

def test_free_download_not_available_without_enough_runs(client):
    """GET /free/download returns 404 when fewer than FREE_LAG runs exist."""
    client.post("/runs/create", json={"seed": 1, "steps": 3})
    resp = client.get("/free/download")
    assert resp.status_code == 404


def test_free_download_available_after_enough_runs(client):
    """GET /free/download returns a zip when enough runs exist (lag=2)."""
    for i in range(3):
        client.post("/runs/create", json={"seed": i, "steps": 3})
    resp = client.get("/free/download")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"


# ---------------------------------------------------------------------------
# /market
# ---------------------------------------------------------------------------

def test_market_returns_html(client):
    """/market returns HTML content."""
    resp = client.get("/market")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Market" in resp.text


# ---------------------------------------------------------------------------
# /events  and  /ledger
# ---------------------------------------------------------------------------

def test_events_returns_list(client):
    """/events returns a dict with an 'events' list."""
    resp = client.get("/events")
    assert resp.status_code == 200
    assert "events" in resp.json()
    assert isinstance(resp.json()["events"], list)


def test_ledger_returns_list(client):
    """/ledger returns a dict with an 'events' list."""
    resp = client.get("/ledger")
    assert resp.status_code == 200
    assert "events" in resp.json()


def test_ledger_records_run_creation(client):
    """/ledger contains a 'run_created' event after POST /runs/create."""
    client.post("/runs/create", json={"seed": 99, "steps": 2})
    resp = client.get("/ledger")
    events = resp.json()["events"]
    assert any(e["type"] == "run_created" for e in events)


# ---------------------------------------------------------------------------
# /public-key
# ---------------------------------------------------------------------------

def test_public_key_404_when_no_key(client):
    """/public-key returns 404 when no signing key has been generated."""
    resp = client.get("/public-key")
    assert resp.status_code == 404


def test_public_key_html_returns_html(client):
    """/public-key.html returns an HTML page."""
    resp = client.get("/public-key.html")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Public Key" in resp.text


# ---------------------------------------------------------------------------
# /maps
# ---------------------------------------------------------------------------

def test_maps_latest_empty_when_no_file(client):
    """/maps/latest returns empty structure when maps file is absent."""
    resp = client.get("/maps/latest")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("runs") == [] or "runs" in data


def test_maps_all_empty_when_no_file(client):
    """/maps/all returns empty structure when maps file is absent."""
    resp = client.get("/maps/all")
    assert resp.status_code == 200
    data = resp.json()
    assert "runs" in data


# ---------------------------------------------------------------------------
# /assets
# ---------------------------------------------------------------------------

def test_assets_scope_returns_dict(client):
    """/assets/scope returns a dict with owner/allow/deny info."""
    resp = client.get("/assets/scope")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)


def test_assets_discover_returns_run_count(client):
    """POST /assets/discover returns asset map with run count."""
    client.post("/runs/create", json={"seed": 1, "steps": 2})
    resp = client.post("/assets/discover")
    assert resp.status_code == 200
    data = resp.json()
    assert "count" in data
    assert data["count"] >= 1


def test_assets_map_html_returns_html(client):
    """/assets/map.html returns HTML content."""
    client.post("/assets/discover")
    resp = client.get("/assets/map.html")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


# ---------------------------------------------------------------------------
# /players
# ---------------------------------------------------------------------------

def test_players_register(client):
    """POST /players/register registers a player and returns ok."""
    resp = client.post("/players/register", json={"player_id": "player_42"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["player_id"] == "player_42"


def test_players_sync_returns_player_info(client):
    """GET /players/sync/{player_id} returns sync payload."""
    client.post("/players/register", json={"player_id": "p1"})
    resp = client.get("/players/sync/p1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["player_id"] == "p1"
    assert "ts" in data


# ---------------------------------------------------------------------------
# /schedule
# ---------------------------------------------------------------------------

def test_set_schedule_persists_config(client, tmp_path):
    """POST /schedule stores scheduler config and returns it."""
    config = {"enabled": True, "interval_seconds": 300}
    resp = client.post("/schedule", json=config)
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["config"]["enabled"] is True


def test_schedule_stop_creates_stop_file(client, tmp_path):
    """POST /schedule/stop creates the STOP file."""
    resp = client.post("/schedule/stop")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert (tmp_path / "STOP").exists()


# ---------------------------------------------------------------------------
# create run — no body / empty body
# ---------------------------------------------------------------------------

def test_create_run_no_body_uses_defaults(client):
    """POST /runs/create with no body uses default seed/steps."""
    resp = client.post("/runs/create")
    assert resp.status_code == 200
    data = resp.json()
    assert "run_id" in data
    assert data["steps"] == 35  # default
