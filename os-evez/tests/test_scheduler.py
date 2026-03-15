"""Tests for autoclaw.scheduler — get_cfg, disk_mb, prune_old_runs."""
import json
import sys
import tempfile
import time
import os
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from autoclaw.scheduler import get_cfg, disk_mb, prune_old_runs


# ---------------------------------------------------------------------------
# get_cfg
# ---------------------------------------------------------------------------

def test_get_cfg_returns_default_when_no_config_file():
    """get_cfg returns defaults when scheduler_config.json is absent."""
    with tempfile.TemporaryDirectory() as td:
        old = os.environ.get("OG_DATA_DIR")
        os.environ["OG_DATA_DIR"] = td
        try:
            cfg = get_cfg()
        finally:
            if old is None:
                del os.environ["OG_DATA_DIR"]
            else:
                os.environ["OG_DATA_DIR"] = old
    assert cfg["enabled"] is False
    assert "interval_seconds" in cfg
    assert "max_runs" in cfg


def test_get_cfg_loads_from_file():
    """get_cfg reads scheduler_config.json from the data directory."""
    with tempfile.TemporaryDirectory() as td:
        config = {
            "enabled": True,
            "interval_seconds": 120,
            "max_runs": 50,
            "max_disk_mb": 1024,
            "retention_runs": 20,
        }
        Path(td).expanduser()
        cfg_path = Path(td) / "scheduler_config.json"
        cfg_path.write_text(json.dumps(config))
        old = os.environ.get("OG_DATA_DIR")
        os.environ["OG_DATA_DIR"] = td
        try:
            cfg = get_cfg()
        finally:
            if old is None:
                del os.environ["OG_DATA_DIR"]
            else:
                os.environ["OG_DATA_DIR"] = old
    assert cfg["enabled"] is True
    assert cfg["interval_seconds"] == 120
    assert cfg["retention_runs"] == 20


def test_get_cfg_default_enabled_is_false():
    """Default config disables the scheduler."""
    with tempfile.TemporaryDirectory() as td:
        old = os.environ.get("OG_DATA_DIR")
        os.environ["OG_DATA_DIR"] = td
        try:
            cfg = get_cfg()
        finally:
            if old is None:
                del os.environ["OG_DATA_DIR"]
            else:
                os.environ["OG_DATA_DIR"] = old
    assert cfg.get("enabled") is False


# ---------------------------------------------------------------------------
# disk_mb
# ---------------------------------------------------------------------------

def test_disk_mb_empty_dir():
    """disk_mb returns 0.0 for an empty directory."""
    with tempfile.TemporaryDirectory() as td:
        result = disk_mb(Path(td))
        assert result == 0.0


def test_disk_mb_single_file():
    """disk_mb accounts for a single file's size."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # Write exactly 1 MiB
        (td / "bigfile.bin").write_bytes(b"x" * 1024 * 1024)
        result = disk_mb(td)
        assert abs(result - 1.0) < 0.01


def test_disk_mb_nested_files():
    """disk_mb sums sizes recursively across subdirectories."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        sub = td / "sub"
        sub.mkdir()
        (td / "a.txt").write_bytes(b"A" * 512 * 1024)   # 0.5 MiB
        (sub / "b.txt").write_bytes(b"B" * 512 * 1024)  # 0.5 MiB
        result = disk_mb(td)
        assert abs(result - 1.0) < 0.01


def test_disk_mb_multiple_small_files():
    """disk_mb correctly sums many small files."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for i in range(10):
            (td / f"f{i}.txt").write_bytes(b"Z" * 1024)  # 1 KiB each = 10 KiB total
        result = disk_mb(td)
        assert abs(result - 10 / 1024) < 0.001


# ---------------------------------------------------------------------------
# prune_old_runs
# ---------------------------------------------------------------------------

def test_prune_old_runs_keeps_newest():
    """prune_old_runs removes oldest directories, keeping only 'keep' newest."""
    with tempfile.TemporaryDirectory() as td:
        runs_dir = Path(td) / "runs"
        runs_dir.mkdir()
        # Create 5 run dirs with different mtimes
        for i in range(5):
            d = runs_dir / f"run_{i:03d}"
            d.mkdir()
            (d / "data.txt").write_text(f"run {i}")
            # Space out mtimes to ensure ordering
            os.utime(d, (time.time() + i, time.time() + i))

        prune_old_runs(runs_dir, keep=3)
        remaining = sorted(d.name for d in runs_dir.iterdir() if d.is_dir())
        assert len(remaining) == 3
        # The 3 newest should be kept: run_002, run_003, run_004
        assert "run_002" in remaining
        assert "run_003" in remaining
        assert "run_004" in remaining


def test_prune_old_runs_noop_when_under_limit():
    """prune_old_runs does nothing when the directory count is within limit."""
    with tempfile.TemporaryDirectory() as td:
        runs_dir = Path(td) / "runs"
        runs_dir.mkdir()
        for i in range(3):
            (runs_dir / f"run_{i}").mkdir()

        prune_old_runs(runs_dir, keep=5)
        remaining = list(runs_dir.iterdir())
        assert len(remaining) == 3


def test_prune_old_runs_exact_limit():
    """prune_old_runs keeps all dirs when count equals keep."""
    with tempfile.TemporaryDirectory() as td:
        runs_dir = Path(td) / "runs"
        runs_dir.mkdir()
        for i in range(4):
            (runs_dir / f"run_{i}").mkdir()

        prune_old_runs(runs_dir, keep=4)
        remaining = list(runs_dir.iterdir())
        assert len(remaining) == 4


def test_prune_old_runs_empty_dir():
    """prune_old_runs handles an empty runs directory without error."""
    with tempfile.TemporaryDirectory() as td:
        runs_dir = Path(td) / "runs"
        runs_dir.mkdir()
        prune_old_runs(runs_dir, keep=10)  # should not raise
        assert list(runs_dir.iterdir()) == []


def test_prune_old_runs_keep_zero():
    """prune_old_runs with keep=0 removes all directories."""
    with tempfile.TemporaryDirectory() as td:
        runs_dir = Path(td) / "runs"
        runs_dir.mkdir()
        for i in range(3):
            d = runs_dir / f"run_{i}"
            d.mkdir()
            (d / "file.txt").write_text("data")

        prune_old_runs(runs_dir, keep=0)
        assert list(runs_dir.iterdir()) == []
