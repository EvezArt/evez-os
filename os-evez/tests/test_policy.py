"""Tests for openclaw.policy — YAML allowlist loader + capability enforcer."""
import sys
import tempfile
import json
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openclaw.policy import (
    load_policy,
    check_kill_switch,
    assert_fs_read,
    assert_fs_write,
    assert_shell,
    DEFAULT_POLICY,
)


# ---------------------------------------------------------------------------
# load_policy
# ---------------------------------------------------------------------------

def test_load_policy_returns_default_when_no_path():
    """load_policy returns DEFAULT_POLICY when called without arguments."""
    policy = load_policy()
    assert policy == DEFAULT_POLICY


def test_load_policy_returns_default_when_path_missing():
    """load_policy returns DEFAULT_POLICY when given a non-existent path."""
    policy = load_policy(Path("/nonexistent/policy.yaml"))
    assert policy == DEFAULT_POLICY


def test_load_policy_from_yaml_file():
    """load_policy correctly loads a custom YAML policy file."""
    yaml_content = """
capabilities:
  FS_READ:
    allow_paths:
      - "./custom_read"
  FS_WRITE:
    allow_paths:
      - "./custom_write"
  SHELL:
    allow_commands:
      - ls
  NET_OUT:
    enabled: false
kill_switch:
  stop_file: "./state/STOP"
budgets:
  max_runtime_seconds: 600
  max_disk_mb: 256
  max_net_mb: 0
"""
    with tempfile.TemporaryDirectory() as td:
        policy_path = Path(td) / "policy.yaml"
        policy_path.write_text(yaml_content)
        policy = load_policy(policy_path)
        assert policy["capabilities"]["FS_READ"]["allow_paths"] == ["./custom_read"]
        assert policy["budgets"]["max_runtime_seconds"] == 600


def test_default_policy_has_expected_capabilities():
    """DEFAULT_POLICY contains all required capability keys."""
    caps = DEFAULT_POLICY["capabilities"]
    assert "FS_READ" in caps
    assert "FS_WRITE" in caps
    assert "SHELL" in caps
    assert "NET_OUT" in caps


# ---------------------------------------------------------------------------
# check_kill_switch
# ---------------------------------------------------------------------------

def test_check_kill_switch_absent():
    """check_kill_switch returns False when STOP file does not exist."""
    with tempfile.TemporaryDirectory() as td:
        result = check_kill_switch(DEFAULT_POLICY, Path(td))
        assert result is False


def test_check_kill_switch_present():
    """check_kill_switch returns True when STOP file exists."""
    with tempfile.TemporaryDirectory() as td:
        stop = Path(td) / "STOP"
        stop.touch()
        result = check_kill_switch(DEFAULT_POLICY, Path(td))
        assert result is True


# ---------------------------------------------------------------------------
# assert_fs_read
# ---------------------------------------------------------------------------

def test_assert_fs_read_allowed_path():
    """assert_fs_read returns True for paths under allowed prefixes."""
    assert assert_fs_read(DEFAULT_POLICY, "./runs/some_run") is True
    assert assert_fs_read(DEFAULT_POLICY, "./fixtures/img.png") is True
    assert assert_fs_read(DEFAULT_POLICY, "./state/config") is True


def test_assert_fs_read_denied_path():
    """assert_fs_read returns False for paths outside allowed prefixes."""
    assert assert_fs_read(DEFAULT_POLICY, "/etc/passwd") is False
    assert assert_fs_read(DEFAULT_POLICY, "/tmp/evil") is False
    assert assert_fs_read(DEFAULT_POLICY, "../secret") is False


def test_assert_fs_read_exact_prefix():
    """assert_fs_read is prefix-based, not exact match."""
    assert assert_fs_read(DEFAULT_POLICY, "./runs") is True
    assert assert_fs_read(DEFAULT_POLICY, "./runs/") is True
    assert assert_fs_read(DEFAULT_POLICY, "./runs/deep/nested/file.txt") is True


# ---------------------------------------------------------------------------
# assert_fs_write
# ---------------------------------------------------------------------------

def test_assert_fs_write_allowed_path():
    """assert_fs_write returns True for paths under allowed write prefixes."""
    assert assert_fs_write(DEFAULT_POLICY, "./runs/output.txt") is True
    assert assert_fs_write(DEFAULT_POLICY, "./state/data.json") is True


def test_assert_fs_write_denied_path():
    """assert_fs_write returns False for paths outside allowed write prefixes."""
    assert assert_fs_write(DEFAULT_POLICY, "/tmp/evil") is False
    assert assert_fs_write(DEFAULT_POLICY, "./fixtures/img.png") is False
    assert assert_fs_write(DEFAULT_POLICY, "/etc/cron.d/evil") is False


# ---------------------------------------------------------------------------
# assert_shell
# ---------------------------------------------------------------------------

def test_assert_shell_allowed_command():
    """assert_shell returns True for commands in the allow-list."""
    assert assert_shell(DEFAULT_POLICY, "ls -la") is True
    assert assert_shell(DEFAULT_POLICY, "cat file.txt") is True
    assert assert_shell(DEFAULT_POLICY, "echo hello") is True
    assert assert_shell(DEFAULT_POLICY, "python script.py") is True
    assert assert_shell(DEFAULT_POLICY, "ffmpeg -i in.mp4 out.mp3") is True


def test_assert_shell_denied_command():
    """assert_shell returns False for commands not in the allow-list."""
    assert assert_shell(DEFAULT_POLICY, "rm -rf /") is False
    assert assert_shell(DEFAULT_POLICY, "curl http://evil.com") is False
    assert assert_shell(DEFAULT_POLICY, "bash -c 'evil'") is False


def test_assert_shell_empty_command():
    """assert_shell returns False for an empty command string."""
    assert assert_shell(DEFAULT_POLICY, "") is False
    assert assert_shell(DEFAULT_POLICY, "   ") is False


def test_assert_shell_custom_policy():
    """assert_shell uses the provided policy's allow-list."""
    custom = {"capabilities": {"SHELL": {"allow_commands": ["git", "make"]}}}
    assert assert_shell(custom, "git status") is True
    assert assert_shell(custom, "make build") is True
    assert assert_shell(custom, "ls -la") is False
