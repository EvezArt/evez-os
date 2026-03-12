"""Tests for evezos.verify — full run verification."""
import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evezos.spine import Spine
from evezos.manifest import build_manifest
from evezos.verify import verify_run


def _make_valid_run(run_dir: Path, spine_events: int = 5) -> dict:
    """Create a fully valid run directory and return the manifest."""
    sp = Spine(run_dir / "spine.jsonl")
    for i in range(spine_events):
        sp.append("step", {"i": i})
    events = sp.read_all()
    mf = build_manifest(run_dir.name, run_dir, events)
    (run_dir / "index.html").write_text("<html>test</html>")
    events2 = sp.read_all()
    mf2 = build_manifest(run_dir.name, run_dir, events2)
    (run_dir / "manifest.json").write_text(json.dumps(mf2))
    # Create provenance bundle
    prov_dir = run_dir / "provenance"
    prov_dir.mkdir(exist_ok=True)
    bundle = {"run_id": run_dir.name, "root_hash": mf2["root_hash"]}
    (prov_dir / "bundle_manifest.json").write_text(json.dumps(bundle))
    return mf2


def test_verify_run_valid():
    """verify_run returns ok=True for a fully valid run."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run_valid"
        run_dir.mkdir()
        _make_valid_run(run_dir)
        result = verify_run(run_dir)
        assert result["ok"] is True
        assert result["run_id"] == "run_valid"
        assert "checks" in result


def test_verify_run_checks_structure():
    """verify_run result contains chain, manifest, and provenance checks."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run_struct"
        run_dir.mkdir()
        _make_valid_run(run_dir)
        result = verify_run(run_dir)
        assert "chain" in result["checks"]
        assert "manifest" in result["checks"]
        assert "provenance" in result["checks"]
        for check in result["checks"].values():
            assert "ok" in check
            assert "msg" in check


def test_verify_run_missing_spine():
    """verify_run chain check fails when spine.jsonl is absent."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run_no_spine"
        run_dir.mkdir()
        # Create manifest.json without spine
        (run_dir / "manifest.json").write_text(json.dumps({"files": {}}))
        (run_dir / "provenance").mkdir()
        (run_dir / "provenance" / "bundle_manifest.json").write_text("{}")
        result = verify_run(run_dir)
        assert result["checks"]["chain"]["ok"] is False
        assert "missing" in result["checks"]["chain"]["msg"]


def test_verify_run_missing_manifest():
    """verify_run manifest check fails when manifest.json is absent."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run_no_manifest"
        run_dir.mkdir()
        sp = Spine(run_dir / "spine.jsonl")
        sp.append("event", {"x": 1})
        (run_dir / "provenance").mkdir()
        (run_dir / "provenance" / "bundle_manifest.json").write_text("{}")
        result = verify_run(run_dir)
        assert result["checks"]["manifest"]["ok"] is False
        assert result["ok"] is False


def test_verify_run_missing_provenance():
    """verify_run provenance check fails when bundle_manifest.json is absent."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run_no_prov"
        run_dir.mkdir()
        _make_valid_run(run_dir)
        # Remove provenance
        import shutil
        shutil.rmtree(run_dir / "provenance")
        result = verify_run(run_dir)
        assert result["checks"]["provenance"]["ok"] is False
        assert result["ok"] is False


def test_verify_run_corrupted_spine():
    """verify_run chain check fails when spine chain is broken."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run_bad_chain"
        run_dir.mkdir()
        _make_valid_run(run_dir)
        # Corrupt the spine by appending a tampered event
        spine_path = run_dir / "spine.jsonl"
        lines = spine_path.read_text().splitlines()
        # Tamper with first event's data
        first = json.loads(lines[0])
        first["data"]["i"] = 999  # alter data without updating chain_hash
        lines[0] = json.dumps(first)
        spine_path.write_text("\n".join(lines) + "\n")
        result = verify_run(run_dir)
        assert result["checks"]["chain"]["ok"] is False


def test_verify_run_ok_flag_aggregates_all_checks():
    """ok is False if any single check fails."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run_partial"
        run_dir.mkdir()
        _make_valid_run(run_dir)
        # Remove only provenance to make one check fail
        import shutil
        shutil.rmtree(run_dir / "provenance")
        result = verify_run(run_dir)
        # chain and manifest should be OK, provenance not
        assert result["checks"]["chain"]["ok"] is True
        assert result["checks"]["manifest"]["ok"] is True
        assert result["checks"]["provenance"]["ok"] is False
        assert result["ok"] is False


def test_verify_run_empty_spine():
    """verify_run handles an empty spine (zero events) gracefully."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run_empty_spine"
        run_dir.mkdir()
        # Write empty spine file
        (run_dir / "spine.jsonl").write_text("")
        mf = {"files": {}}
        (run_dir / "manifest.json").write_text(json.dumps(mf))
        (run_dir / "provenance").mkdir()
        (run_dir / "provenance" / "bundle_manifest.json").write_text("{}")
        result = verify_run(run_dir)
        assert result["checks"]["chain"]["ok"] is True
