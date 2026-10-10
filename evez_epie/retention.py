"""Budgeted information retention: optimize active-index utility without deleting evidence."""
from __future__ import annotations

import math
from typing import Any, Iterable, Mapping
from .kernel import retention_score


def select_hot_index(
    items: Iterable[Mapping[str, Any]],
    budget_bytes: int,
    *,
    now_seconds: float,
) -> dict[str, Any]:
    """Select content groups maximizing retained retrieval utility under a byte budget.

    Uses a Pareto-frontier 0/1 knapsack, not a greedy value-density approximation.
    Exact content hashes share one indexed payload; every source ID in a selected
    group remains represented as a source reference. Unselected originals are
    archival, not deleted. Runtime depends on the size of the Pareto frontier.
    """
    if isinstance(budget_bytes, bool) or not isinstance(budget_bytes, int) or budget_bytes < 0:
        raise ValueError("budget_bytes must be a non-negative integer")
    if not math.isfinite(now_seconds):
        raise ValueError("now_seconds must be finite")
    items = list(items)
    seen_ids = set()
    for item in items:
        item_id = str(item.get("id", ""))
        if not item_id:
            raise ValueError("Every item requires a non-empty id")
        if item_id in seen_ids:
            raise ValueError(f"Duplicate evidence item id: {item_id}")
        seen_ids.add(item_id)
    groups: dict[str, list[Mapping[str, Any]]] = {}
    for item in items:
        item_id = str(item.get("id", ""))
        if not item_id:
            raise ValueError("Every item requires a non-empty id")
        digest = item.get("content_hash")
        key = "hash:" + digest if isinstance(digest, str) and digest else "id:" + item_id
        groups.setdefault(key, []).append(item)

    candidates = []
    for key, refs in sorted(groups.items()):
        sizes = [max(0, int(ref.get("storage_bytes", 0))) for ref in refs]
        cost = max(sizes, default=0)
        scores = []
        for ref in refs:
            age = max(0.0, now_seconds - float(ref["created_at_seconds"]))
            scores.append(retention_score(
                decision_value=float(ref.get("decision_value", 1.0)),
                reliability=float(ref.get("reliability", 0.5)),
                novelty=float(ref.get("novelty", 1.0)),
                age_seconds=age,
                half_life_seconds=ref.get("half_life_seconds"),
            ))
        # Exact duplicate bytes add references, not duplicated information value.
        value = max(scores, default=0.0)
        ids = tuple(sorted(str(ref["id"]) for ref in refs))
        candidates.append({"key": key, "cost": cost, "value": value, "ids": ids})

    # State is (bytes_used, utility, selected_candidate_indexes).
    frontier = [(0, 0.0, tuple())]
    for index, candidate in enumerate(candidates):
        additions = []
        for used, value, selected in frontier:
            next_used = used + candidate["cost"]
            if next_used <= budget_bytes:
                additions.append((next_used, value + candidate["value"], selected + (index,)))
        merged = frontier + additions
        # For each exact byte cost, retain the highest value, with stable tie-break.
        best_by_cost = {}
        for state in merged:
            used, value, selected = state
            old = best_by_cost.get(used)
            if old is None or value > old[1] + 1e-15 or (
                abs(value - old[1]) <= 1e-15 and selected < old[2]
            ):
                best_by_cost[used] = state
        # Pareto prune: a state is dominated if fewer/equal bytes have greater/equal value.
        pruned = []
        best_value = -1.0
        for used in sorted(best_by_cost):
            state = best_by_cost[used]
            if state[1] > best_value + 1e-15:
                pruned.append(state)
                best_value = state[1]
        frontier = pruned

    winner = max(frontier, key=lambda s: (s[1], -s[0], tuple(-i for i in s[2])))
    used, value, selected = winner
    chosen = [candidates[i] for i in selected]
    selected_ids = sorted(source_id for group in chosen for source_id in group["ids"])
    return {
        "budget_bytes": budget_bytes,
        "used_bytes": used,
        "retained_utility": value,
        "selected_content_groups": [
            {"content_key": group["key"], "storage_bytes": group["cost"],
             "retention_utility": group["value"], "source_ids": list(group["ids"])}
            for group in chosen
        ],
        "selected_source_ids": selected_ids,
        "archival_only_source_ids": sorted(
            str(ref["id"]) for ref in items if str(ref.get("id", "")) not in selected_ids
        ),
        "policy": "No raw evidence is deleted; selection controls hot-index residency only.",
    }
