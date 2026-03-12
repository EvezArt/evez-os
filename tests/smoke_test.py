"""
tests/smoke_test.py
Root-level smoke tests for tools/evez.py and tools/run_all.py.
Run from repo root: python -m pytest tests/
"""
import sys
import importlib
import pathlib
import tempfile
import os
import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _add_root():
    r = str(REPO_ROOT)
    if r not in sys.path:
        sys.path.insert(0, r)


# ---------------------------------------------------------------------------
# Import smoke
# ---------------------------------------------------------------------------

def test_evez_importable():
    """tools/evez.py must be importable without side effects."""
    _add_root()
    import tools.evez  # noqa: F401
    assert hasattr(tools.evez, 'cmd_init')
    assert hasattr(tools.evez, 'cmd_lint')
    assert hasattr(tools.evez, 'cmd_play')
    assert hasattr(tools.evez, 'cmd_verify')


def test_run_all_importable():
    """tools/run_all.py must be importable without executing."""
    _add_root()
    import tools.run_all  # noqa: F401
    assert hasattr(tools.run_all, 'seed_demo')
    assert hasattr(tools.run_all, '_read_jsonl')
    assert hasattr(tools.run_all, '_append_jsonl')


# ---------------------------------------------------------------------------
# init subcommand
# ---------------------------------------------------------------------------

def test_evez_init_seeds_spine(tmp_path, monkeypatch):
    """evez init creates spine/EVENT_SPINE.jsonl and spine/ARG_SPINE.jsonl."""
    _add_root()
    import tools.evez as evez
    # Redirect REPO_ROOT to tmp_path so we don't pollute the real repo
    monkeypatch.setattr(evez, 'REPO_ROOT', tmp_path)
    import argparse
    args = argparse.Namespace()
    rc = evez.cmd_init(args)
    assert rc == 0
    assert (tmp_path / 'spine' / 'EVENT_SPINE.jsonl').exists()
    assert (tmp_path / 'spine' / 'EVENT_SPINE.jsonl').stat().st_size > 0
    assert (tmp_path / 'spine' / 'ARG_SPINE.jsonl').exists()


def test_evez_init_idempotent(tmp_path, monkeypatch):
    """Running init twice does not corrupt existing spines."""
    _add_root()
    import tools.evez as evez
    monkeypatch.setattr(evez, 'REPO_ROOT', tmp_path)
    import argparse
    args = argparse.Namespace()
    evez.cmd_init(args)
    spine_path = tmp_path / 'spine' / 'EVENT_SPINE.jsonl'
    content_before = spine_path.read_text()
    evez.cmd_init(args)  # second run
    content_after = spine_path.read_text()
    assert content_before == content_after, "init must not double-write existing spine"


# ---------------------------------------------------------------------------
# lint subcommand
# ---------------------------------------------------------------------------

def test_evez_lint_no_spine(tmp_path, monkeypatch):
    """lint returns 0 when spine/ does not exist (not an error)."""
    _add_root()
    import tools.evez as evez
    monkeypatch.setattr(evez, 'REPO_ROOT', tmp_path)
    import argparse
    rc = evez.cmd_lint(argparse.Namespace())
    assert rc == 0


def test_evez_lint_valid_syntax(tmp_path, monkeypatch):
    """lint passes on a valid .py spine module."""
    _add_root()
    import tools.evez as evez
    monkeypatch.setattr(evez, 'REPO_ROOT', tmp_path)
    spine_dir = tmp_path / 'spine'
    spine_dir.mkdir()
    (spine_dir / 'watch_001.py').write_text('print("ok")\n')
    import argparse
    rc = evez.cmd_lint(argparse.Namespace())
    assert rc == 0


def test_evez_lint_catches_syntax_error(tmp_path, monkeypatch):
    """lint returns non-zero on a .py file with a syntax error."""
    _add_root()
    import tools.evez as evez
    monkeypatch.setattr(evez, 'REPO_ROOT', tmp_path)
    spine_dir = tmp_path / 'spine'
    spine_dir.mkdir()
    (spine_dir / 'broken.py').write_text('def foo(:\n    pass\n')
    import argparse
    rc = evez.cmd_lint(argparse.Namespace())
    assert rc != 0, "lint must fail on syntax error"


# ---------------------------------------------------------------------------
# run_all seed
# ---------------------------------------------------------------------------

def test_run_all_seed_creates_files(tmp_path, monkeypatch):
    """run_all.seed_demo creates spine files when they don't exist."""
    _add_root()
    import tools.run_all as ra
    monkeypatch.setattr(ra, 'SPINE_DIR', str(tmp_path / 'spine'))
    monkeypatch.setattr(ra, 'EVENT_SPINE', str(tmp_path / 'spine' / 'EVENT_SPINE.jsonl'))
    monkeypatch.setattr(ra, 'ARG_SPINE', str(tmp_path / 'spine' / 'ARG_SPINE.jsonl'))
    ra._ensure_files()
    result = ra.seed_demo()
    assert result is not False  # seed ran
    import json
    events = ra._read_jsonl(str(tmp_path / 'spine' / 'EVENT_SPINE.jsonl'))
    assert len(events) > 0
    for ev in events:
        assert 'timestamp' in ev
        assert 'type' in ev
