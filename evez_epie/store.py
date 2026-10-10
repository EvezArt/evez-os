"""Durable append-only JSONL ledger for the local EPIE evidence kernel.

Uses POSIX flock (Termux/Linux/macOS), private file permissions and fsync.
Incomplete writes or invalid history fail closed; nothing truncates or repairs
the evidence file automatically. Appends use a metadata-invalidated in-memory
cache for speed; explicit load/verify always re-read and validate the entire file.
"""
from __future__ import annotations

import errno
import json
import os
import stat
from pathlib import Path
from typing import Any, Mapping

import rfc8785

from .kernel import EventLedger


class JsonlLedgerStore:
    """Process-serialized append-only store with explicit full-history verification."""

    def __init__(self, path: str | os.PathLike[str]):
        if not str(path):
            raise ValueError("Ledger path must not be empty")
        self.path = Path(path).expanduser().absolute()
        self.lock_path = self.path.with_name(self.path.name + ".lock")
        self._cache: EventLedger | None = None
        self._cached_signature = None

    @staticmethod
    def _signature(path: Path):
        try:
            result = os.stat(path, follow_symlinks=False)
        except FileNotFoundError:
            return None
        if stat.S_ISLNK(result.st_mode):
            raise ValueError(f"Refusing symlink path: {path}")
        if not stat.S_ISREG(result.st_mode):
            raise ValueError(f"Ledger path must be a regular file: {path}")
        return (result.st_dev, result.st_ino, result.st_size, result.st_mtime_ns)

    def _open_no_follow(self, path: Path, flags: int, mode: int = 0o600) -> int:
        no_follow = getattr(os, "O_NOFOLLOW", 0)
        nonblock = getattr(os, "O_NONBLOCK", 0)
        return os.open(str(path), flags | no_follow | nonblock, mode)

    def _read_unlocked(self) -> EventLedger:
        try:
            fd = self._open_no_follow(self.path, os.O_RDONLY)
        except FileNotFoundError:
            return EventLedger()
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                raise ValueError("Refusing to follow a symlink for the ledger file") from exc
            raise
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError("Ledger must be a regular file")
            with os.fdopen(fd, "rb") as stream:
                fd = -1
                raw = stream.read()
        finally:
            if fd >= 0:
                os.close(fd)
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
        return _PosixFileLock(self.lock_path, self.path.parent, self._open_no_follow)

    def load(self) -> EventLedger:
        """Force a full disk read and hash-chain validation, then refresh the cache."""
        with self._exclusive():
            ledger = self._read_unlocked()
            self._cache = ledger
            self._cached_signature = self._signature(self.path)
            # Never expose the cached mutable object to callers.
            return EventLedger(ledger.events)

    def append(self, event_type: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._exclusive():
            signature = self._signature(self.path)
            if self._cache is None or signature != self._cached_signature:
                self._cache = self._read_unlocked()
                self._cached_signature = self._signature(self.path)
            ledger = self._cache
            event = ledger.append(event_type, payload)
            encoded = rfc8785.dumps(event) + b"\n"
            file_existed = signature is not None
            fd = self._open_no_follow(self.path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
            try:
                if not stat.S_ISREG(os.fstat(fd).st_mode):
                    raise ValueError("Ledger append target must be a regular file")
                os.fchmod(fd, 0o600)
                remaining = memoryview(encoded)
                while remaining:
                    written = os.write(fd, remaining)
                    if written <= 0:
                        raise OSError("Short write while appending EPIE ledger")
                    remaining = remaining[written:]
                os.fsync(fd)
            except Exception:
                # The cache has already advanced. Invalidate it so the next
                # operation re-reads disk and detects any partial line.
                self._cache = None
                self._cached_signature = None
                raise
            finally:
                os.close(fd)
            try:
                if not file_existed and hasattr(os, "O_DIRECTORY"):
                    directory_fd = os.open(str(self.path.parent), os.O_RDONLY | os.O_DIRECTORY)
                    try:
                        os.fsync(directory_fd)
                    finally:
                        os.close(directory_fd)
                self._cached_signature = self._signature(self.path)
                return event
            except Exception:
                self._cache = None
                self._cached_signature = None
                raise

    def verify(self) -> tuple[bool, str]:
        try:
            ledger = self.load()
        except Exception as exc:
            return False, f"{type(exc).__name__}: {exc}"
        return ledger.verify()

    def replay(self) -> dict[str, Any]:
        return self.load().replay()


class _PosixFileLock:
    """Cross-process advisory lock, supported by Termux/Linux/macOS."""

    def __init__(self, lock_path: Path, parent: Path, open_no_follow):
        self.lock_path = lock_path
        self.parent = parent
        self.open_no_follow = open_no_follow
        self.fd = None

    def __enter__(self):
        try:
            import fcntl
        except ImportError as exc:
            raise RuntimeError(
                "Cross-process ledger locking requires POSIX fcntl (Termux/Linux/macOS)"
            ) from exc
        self.parent.mkdir(parents=True, exist_ok=True)
        self.fd = self.open_no_follow(self.lock_path, os.O_RDWR | os.O_CREAT, 0o600)
        if not stat.S_ISREG(os.fstat(self.fd).st_mode):
            os.close(self.fd)
            self.fd = None
            raise ValueError("Lock path must be a regular file")
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
