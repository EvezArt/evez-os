"""Before/action/after observation."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .canonical import sha256_hex

@dataclass(frozen=True)
class Observation:
    before: dict[str, Any]
    after: dict[str, Any]
    delta: dict[str, Any]
    before_hash: str
    after_hash: str

def observe(before: dict[str, Any], after: dict[str, Any]) -> Observation:
    delta: dict[str, Any] = {}
    for key in sorted(set(before) | set(after)):
        bv, av = before.get(key), after.get(key)
        if bv != av or key not in before or key not in after:
            delta[key] = {"before": bv, "after": av}
    return Observation(dict(before), dict(after), delta, sha256_hex(before), sha256_hex(after))
