"""
evez_tasks_worker_patch.py
==========================
Constitutional Rule #2 enforcement patch.
Resolves: evez-os#3

Apply this guard in evez_tasks_worker.py before every spine append.
Import assert_falsifier and call it before spine.append(payload).

Usage:
  from evez_tasks_worker_patch import assert_falsifier, ConstitutionalViolation
  try:
      assert_falsifier(payload)
  except ConstitutionalViolation as e:
      return JSONResponse(status_code=400, content={"error": str(e)})
"""

from typing import Any


class ConstitutionalViolation(ValueError):
    """Raised when a payload violates a constitutional rule."""
    pass


def assert_falsifier(payload: dict[str, Any]) -> None:
    """
    Constitutional Rule #2: No claim without a falsifier.

    Accepted field names (in priority order):
      'falsifier', 'falsifier_tx', 'tx_id', 'proof'

    Raises ConstitutionalViolation if none found or all are empty/null.
    """
    FALSIFIER_FIELDS = ("falsifier", "falsifier_tx", "tx_id", "proof")
    for field in FALSIFIER_FIELDS:
        val = payload.get(field)
        if val is not None and str(val).strip():
            return  # valid falsifier found

    kind = payload.get("kind", "unknown")
    raise ConstitutionalViolation(
        f"Constitutional Rule #2 violation: event payload missing falsifier field. "
        f"kind={kind!r}. Accepted fields: {FALSIFIER_FIELDS}. "
        f"Spine append REJECTED."
    )


def safe_spine_append(payload: dict[str, Any], spine_append_fn, math_layer: bool = False) -> Any:
    """
    Wraps spine_append_fn with Rule #2 enforcement.
    math_layer=True bypasses guard (A012 doctrine: local JSONL writes exempt).
    """
    if math_layer:
        return spine_append_fn(payload)
    assert_falsifier(payload)
    return spine_append_fn(payload)
