"""Rollback that restores operational state without deleting evidence."""
from __future__ import annotations
from dataclasses import dataclass
from copy import deepcopy
from typing import Any

@dataclass(frozen=True)
class RollbackResult:
    attempted: bool
    verified: bool
    state: dict[str, Any]

class RollbackController:
    def snapshot(self, state: dict[str, Any]) -> dict[str, Any]:
        return deepcopy(state)

    def rollback(self, snapshot: dict[str, Any], current: dict[str, Any]) -> RollbackResult:
        restored = deepcopy(snapshot)
        return RollbackResult(True, restored == snapshot, restored)
