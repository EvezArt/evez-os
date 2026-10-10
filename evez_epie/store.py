"""Durable, append-only JSONL storage for the local EPIE evidence ledger.

POSIX advisory locking targets Termux/Linux/macOS. A partial final write is
reported as corruption and is never silently truncated or repaired.
"""
from __future__ import annotations

import errno
import json
import os
from pathlib import Path
from typing import Any, Mapping

import rfc8785

from .kernel import EventLedger


class JsonlLedgerStore:
    """Process-serialized append-only store with fsync and fail-closed replay."""

    def __init__(self, path: str | os.PathLike[str]):
        if not str(path):
            raise ValueError("Ledger path must not be empty")
        self.path = Path(path).expanduser().absolute()
        self.lock_path = self.path.with_name(self.path.name + ".lock")

    def _open_no_follow(self, path: Path, flags: int, mode: int = 0o600) -> int:
        no_follow = getattr(os, "O_NOFOLLOW", 0)
        return os.open(str(path), flags | no_follow, mode)

    def _read_unlocked(self) -> EventLedger:
        try:
            fd = self._open_no_follow(self.path, os.O_RDONLY)
        except FileNotFoundError:
            return EventLedger()
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                raise ValueError("Refusing to follow a symlink for the ledger file") from exc
            raise
        with os.fdopen(fd, "rb") as stream:
            raw = stream.read()
        if raw and not raw.endswith(b"\n"):
            raise ValueError("Ledger has an incomplete final line; refusing automatic repair")
        events = []
        for line_number, line in enumerate(raw.splitlines(), start=1):
            if not line:
                raise ValueError(f"Ledger contains a blank line at {line_number}")
            try:
                event = json.loads(line.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError(f"Invalid JSONL record at line {line_number}") from exc
            if not isinstance(event, dict):
                raise ValueError(f"Ledger record at line {line_number} must be a JSON object")
            events.append(event)
        return EventLedger(events)

    def _exclusive(self):
        """Small context manager without third-party lock dependencies."""
        return _PosixFileLock(self.lock_path, self.path.parent, self._open_no_follow)

    def load(self) -> EventLedger:
        with self._exclusive():
            return self._read_unlocked()

    def append(self, event_type: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._exclusive():
            ledger = self._read_unlocked()
            event = ledger.append(event_type, payload)
            encoded = rfc8785.dumps(event) + b"\n"
            file_existed = self.path.exists()
            fd = self._open_no_follow(self.path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
            try:
                os.fchmod(fd, 0o600)
                remaining = memoryview(encoded)
                while remaining:
                    written = os.write(fd, remaining)
                    if written <= 0:
                        raise OSError("Short write while appending EPIE ledger")
                    remaining = remaining[written:]
                os.fsync(fd)
            finally:
                os.close(fd)
            if not file_existed and hasattr(os, "O_DIRECTORY"):
                directory_fd = os.open(str(self.path.parent), os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
            return event

    def verify(self) -> tuple[bool, str]:
        try:
            ledger = self.load()
        except Exception as exc:
            return False, f"{type(exc).__name__}: {exc}"
        return ledger.verify()

    def replay(self) -> dict[str, Any]:
        return self.load().replay()


class _PosixFileLock:
    """Context manager using POSIX flock to serialize independent processes."""

    def __init__(self, lock_path: Path, parent: Path, open_no_follow):
        self.lock_path = lock_path
        self.parent = parent
        self.open_no_follow = open_no_follow
        self.fd = None

    def __enter__(self):
        try:
            import fcntl
        except ImportError as exc:
            raise RuntimeError("Cross-process ledger locking requires POSIX fcntl (available on Termux/Linux/macOS)") from exc
        self.parent.mkdir(parents=True, exist_ok=True)
        self.fd = self.open_no_follow(self.lock_path, os.O_RDWR | os.O_CREAT, 0o600)
        os.fchmod(self.fd, 0o600)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX)
        except Exception:
            os.close(self.fd)
            self.fd = None
            raise
        return self

    def __exit__(self, exc_type, exc, traceback):
        import fcntl
        try:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
        finally:
            os.close(self.fd)
            self.fd = None
        return False
