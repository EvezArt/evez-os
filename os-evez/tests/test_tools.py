"""Tests for openclaw.tools — bounded ToolRunner (FS_READ, FS_WRITE, SHELL)."""
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openclaw.tools import ToolRunner
from openclaw.policy import DEFAULT_POLICY


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_runner(tmp_dir: Path) -> ToolRunner:
    """Create a ToolRunner whose data_dir is inside tmp_dir."""
    return ToolRunner(data_dir=tmp_dir)


# ---------------------------------------------------------------------------
# read_file
# ---------------------------------------------------------------------------

def test_read_file_allowed_path(tmp_path, monkeypatch):
    """read_file reads a file under an allowed FS_READ path.

    ToolRunner.read_file(path) calls Path(path).read_text(), which is
    relative to the current working directory.  We therefore temporarily
    change CWD to the temp dir and place the file under ./runs/ so that
    both the policy prefix check and the filesystem read succeed.
    """
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "runs" / "data.txt"
    target.parent.mkdir(parents=True)
    target.write_text("hello world")

    runner = ToolRunner(data_dir=tmp_path)
    content = runner.read_file("./runs/data.txt")
    assert content == "hello world"


def test_read_file_denied_path_raises():
    """read_file raises PermissionError for out-of-scope paths."""
    with tempfile.TemporaryDirectory() as td:
        runner = ToolRunner(data_dir=Path(td))
        with pytest.raises(PermissionError, match="FS_READ denied"):
            runner.read_file("/etc/passwd")


def test_read_file_denied_tmp_path():
    """read_file raises PermissionError for /tmp paths."""
    with tempfile.TemporaryDirectory() as td:
        runner = ToolRunner(data_dir=Path(td))
        with pytest.raises(PermissionError):
            runner.read_file("/tmp/something")


# ---------------------------------------------------------------------------
# write_file
# ---------------------------------------------------------------------------

def test_write_file_allowed_path(tmp_path, monkeypatch):
    """write_file writes content to a file under an allowed FS_WRITE path."""
    monkeypatch.chdir(tmp_path)
    runner = ToolRunner(data_dir=tmp_path)
    runner.write_file("./state/output.txt", "test content")
    written = (tmp_path / "state" / "output.txt").read_text()
    assert written == "test content"


def test_write_file_denied_path_raises():
    """write_file raises PermissionError for out-of-scope paths."""
    with tempfile.TemporaryDirectory() as td:
        runner = ToolRunner(data_dir=Path(td))
        with pytest.raises(PermissionError, match="FS_WRITE denied"):
            runner.write_file("/tmp/evil.txt", "evil")


def test_write_file_creates_parent_dirs(tmp_path, monkeypatch):
    """write_file creates parent directories if they don't exist."""
    monkeypatch.chdir(tmp_path)
    runner = ToolRunner(data_dir=tmp_path)
    nested = "./runs/subdir/deeply/nested.txt"
    runner.write_file(nested, "deep content")
    assert (tmp_path / "runs" / "subdir" / "deeply" / "nested.txt").read_text() == "deep content"


# ---------------------------------------------------------------------------
# run_shell
# ---------------------------------------------------------------------------

def test_run_shell_allowed_command():
    """run_shell executes an allowed shell command and returns stdout."""
    with tempfile.TemporaryDirectory() as td:
        runner = ToolRunner(data_dir=Path(td))
        output = runner.run_shell("echo hello_test")
        assert "hello_test" in output


def test_run_shell_denied_command_raises():
    """run_shell raises PermissionError for commands not in the allow-list."""
    with tempfile.TemporaryDirectory() as td:
        runner = ToolRunner(data_dir=Path(td))
        with pytest.raises(PermissionError, match="SHELL denied"):
            runner.run_shell("rm -rf /")


def test_run_shell_cat_command():
    """run_shell allows 'cat' which is in the default allow-list."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        test_file = td / "test.txt"
        test_file.write_text("cats are allowed")
        runner = ToolRunner(data_dir=td)
        output = runner.run_shell(f"cat {test_file}")
        assert "cats are allowed" in output


# ---------------------------------------------------------------------------
# Kill switch
# ---------------------------------------------------------------------------

def test_kill_switch_stops_all_operations():
    """All tool operations raise RuntimeError when STOP file is present."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        stop_file = td / "STOP"
        stop_file.touch()
        runner = ToolRunner(data_dir=td)
        with pytest.raises(RuntimeError, match="KILL SWITCH"):
            runner.read_file("./runs/anything.txt")


def test_kill_switch_blocks_write():
    """write_file raises RuntimeError when STOP file exists."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "STOP").touch()
        runner = ToolRunner(data_dir=td)
        with pytest.raises(RuntimeError, match="KILL SWITCH"):
            runner.write_file("./state/x.txt", "data")


def test_kill_switch_blocks_shell():
    """run_shell raises RuntimeError when STOP file exists."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "STOP").touch()
        runner = ToolRunner(data_dir=td)
        with pytest.raises(RuntimeError, match="KILL SWITCH"):
            runner.run_shell("echo hi")


# ---------------------------------------------------------------------------
# Call budget
# ---------------------------------------------------------------------------

def test_call_budget_exceeded():
    """ToolRunner raises RuntimeError when call budget is exhausted."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # Build a policy with max_tool_calls = 2
        policy = {
            "capabilities": DEFAULT_POLICY["capabilities"],
            "kill_switch": DEFAULT_POLICY["kill_switch"],
            "budgets": {"max_tool_calls": 2},
        }
        # Inject policy by monkey-patching after construction
        runner = ToolRunner(data_dir=td)
        runner.max_calls = 2
        # First two calls should succeed (echo is in allow-list)
        runner.run_shell("echo 1")
        runner.run_shell("echo 2")
        # Third call must raise
        with pytest.raises(RuntimeError, match="budget exceeded"):
            runner.run_shell("echo 3")


def test_call_count_increments():
    """call_count increments with each successful tool call."""
    with tempfile.TemporaryDirectory() as td:
        runner = ToolRunner(data_dir=Path(td))
        assert runner.call_count == 0
        runner.run_shell("echo a")
        assert runner.call_count == 1
        runner.run_shell("echo b")
        assert runner.call_count == 2
