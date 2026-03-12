"""Tests for evezos.viz — ASCII spine visualizer."""
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evezos.spine import Spine
from evezos.viz import summarize_spine


def test_summarize_spine_nonexistent_file():
    """Returns 'not found' message when path does not exist."""
    result = summarize_spine(Path("/nonexistent/path/spine.jsonl"))
    assert "not found" in result


def test_summarize_spine_empty_file():
    """Handles an empty spine file without error."""
    with tempfile.TemporaryDirectory() as td:
        spine_path = Path(td) / "empty.jsonl"
        spine_path.write_text("")
        result = summarize_spine(spine_path)
        assert "0 events" in result


def test_summarize_spine_contains_event_count():
    """Output reports the correct number of events."""
    with tempfile.TemporaryDirectory() as td:
        spine_path = Path(td) / "spine.jsonl"
        sp = Spine(spine_path)
        for i in range(7):
            sp.append("test_event", {"i": i})
        result = summarize_spine(spine_path)
        assert "7 events" in result


def test_summarize_spine_contains_path():
    """Output includes the spine file path."""
    with tempfile.TemporaryDirectory() as td:
        spine_path = Path(td) / "my_spine.jsonl"
        sp = Spine(spine_path)
        sp.append("ping", {"x": 1})
        result = summarize_spine(spine_path)
        assert "my_spine.jsonl" in result


def test_summarize_spine_shows_event_type():
    """Output includes event types for listed events."""
    with tempfile.TemporaryDirectory() as td:
        spine_path = Path(td) / "spine.jsonl"
        sp = Spine(spine_path)
        sp.append("my_custom_event", {"a": 1})
        result = summarize_spine(spine_path)
        assert "my_custom_event" in result


def test_summarize_spine_shows_chain_hash_prefix():
    """Output includes a prefix of each event's chain hash."""
    with tempfile.TemporaryDirectory() as td:
        spine_path = Path(td) / "spine.jsonl"
        sp = Spine(spine_path)
        evt = sp.append("hash_check", {"v": 42})
        result = summarize_spine(spine_path)
        # The viz shows first 12 chars of hash followed by "..."
        assert evt["chain_hash"][:12] in result


def test_summarize_spine_limits_to_last_ten():
    """Only up to the last 10 events are shown in detail."""
    with tempfile.TemporaryDirectory() as td:
        spine_path = Path(td) / "spine.jsonl"
        sp = Spine(spine_path)
        for i in range(25):
            sp.append("tick", {"i": i})
        result = summarize_spine(spine_path)
        # Count how many event lines appear (lines containing "...")
        detail_lines = [l for l in result.splitlines() if "..." in l]
        assert len(detail_lines) <= 10


def test_summarize_spine_returns_string():
    """summarize_spine always returns a str."""
    with tempfile.TemporaryDirectory() as td:
        spine_path = Path(td) / "spine.jsonl"
        sp = Spine(spine_path)
        sp.append("ev", {})
        result = summarize_spine(spine_path)
        assert isinstance(result, str)
