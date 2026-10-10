"""Deterministic, dependency-aware inference and information-retention primitives.

This is a reference kernel, not a source-authentication system or an autonomous
investigator. Probabilities and likelihoods are inputs that must be justified.
Uses the pinned, dependency-free rfc8785 package for standards-compatible JCS serialization.
"""
from __future__ import annotations
import copy, hashlib, math, time
import rfc8785
from typing import Any, Iterable, Mapping, Sequence

EVENT_TYPES = frozenset({"OBSERVED_FACT", "EVIDENCE_COMMIT", "CHECKPOINT_ISSUED"})

def canonical_json(value: Any) -> str:
    """Return RFC 8785 canonical JSON via the vetted rfc8785 implementation."""
    return rfc8785.dumps(value).decode("utf-8")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(rfc8785.dumps(value)).hexdigest()

def _normalise(weights: Mapping[str, float]) -> dict[str, float]:
    if not weights: raise ValueError("At least one hypothesis is required")
    if any(not math.isfinite(v) or v < 0 for v in weights.values()): raise ValueError("Weights must be finite and non-negative")
    total = math.fsum(weights.values())
    if total <= 0: raise ValueError("Weights sum to zero")
    return {k: v / total for k, v in sorted(weights.items())}

def bayesian_update(prior: Mapping[str, float], evidence: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    """Update in log space; require explicit conditional independence.

    Each evidence item requires id, likelihoods, independence_group, and
    conditional_independence_asserted=True. Repeated groups are rejected so
    derivative sources cannot silently be counted as independent evidence.
    Model a dependent bundle with a defensible joint likelihood.
    """
    p = _normalise(prior); hypotheses = set(p); seen_ids = set(); seen_groups = set()
    logw = {h: math.log(v) if v > 0 else -math.inf for h, v in p.items()}
    for item in evidence:
        eid, group, likelihoods = item.get("id"), item.get("independence_group"), item.get("likelihoods")
        if not isinstance(eid, str) or not eid: raise ValueError("Each evidence item requires a non-empty id")
        if eid in seen_ids: raise ValueError(f"Duplicate evidence id: {eid}")
        seen_ids.add(eid)
        if item.get("conditional_independence_asserted") is not True: raise ValueError(f"Conditional independence not declared for {eid}")
        if not isinstance(group, str) or not group: raise ValueError(f"Missing independence_group for {eid}")
        if group in seen_groups: raise ValueError(f"Repeated dependence group {group!r}; supply a joint likelihood or model dependence explicitly")
        seen_groups.add(group)
        if not isinstance(likelihoods, Mapping) or set(likelihoods) != hypotheses: raise ValueError(f"{eid}: likelihoods must cover exactly the prior hypotheses")
        for h in hypotheses:
            likelihood = likelihoods[h]
            if not isinstance(likelihood, (int, float)) or not math.isfinite(likelihood) or likelihood <= 0 or likelihood > 1:
                raise ValueError(f"{eid}: likelihood for {h} must be in (0, 1]")
            if logw[h] != -math.inf: logw[h] += math.log(likelihood)
    finite = [v for v in logw.values() if math.isfinite(v)]
    if not finite: raise ValueError("All hypotheses have zero posterior support")
    peak = max(finite)
    return _normalise({h: math.exp(v - peak) if math.isfinite(v) else 0.0 for h, v in logw.items()})

def entropy_bits(probabilities: Mapping[str, float]) -> float:
    p = _normalise(probabilities)
    return -math.fsum(v * math.log2(v) for v in p.values() if v > 0)

def expected_information_gain(prior: Mapping[str, float], test: Mapping[str, Any]) -> float:
    """Expected entropy reduction in bits for a complete finite-outcome table."""
    p = _normalise(prior); outcomes = test.get("outcomes")
    if not isinstance(outcomes, Mapping) or not outcomes: raise ValueError("Test requires an outcomes mapping")
    if any(set(row) != set(p) for row in outcomes.values()): raise ValueError("Every outcome must specify every hypothesis")
    for h in p:
        vals = [float(outcomes[o][h]) for o in outcomes]
        if any(not math.isfinite(v) or v < 0 or v > 1 for v in vals): raise ValueError("Outcome likelihoods must be in [0, 1]")
        total = math.fsum(vals)
        if not math.isclose(total, 1.0, rel_tol=1e-9, abs_tol=1e-9): raise ValueError(f"Outcome likelihoods for {h} sum to {total}, not 1")
    before = entropy_bits(p); expected_after = 0.0
    for outcome, row in outcomes.items():
        p_outcome = math.fsum(p[h] * float(row[h]) for h in p)
        if p_outcome == 0: continue
        posterior = _normalise({h: p[h] * float(row[h]) for h in p})
        expected_after += p_outcome * entropy_bits(posterior)
    gain = before - expected_after
    if gain < -1e-9: raise ArithmeticError("Expected information gain became negative")
    return max(0.0, gain)

def rank_tests(prior: Mapping[str, float], tests: Iterable[Mapping[str, Any]], *, cost_weight: float = 1.0, risk_weight: float = 1.0) -> list[dict[str, Any]]:
    """Rank permitted tests by value*IG - weighted cost - weighted risk.

    Cost/risk/value are dimensionless until the application calibrates them.
    This score never grants authorization; tests require permitted=True.
    """
    if not math.isfinite(cost_weight) or not math.isfinite(risk_weight) or cost_weight < 0 or risk_weight < 0: raise ValueError("Weights must be finite and non-negative")
    ranked = []
    for test in tests:
        if test.get("permitted") is not True: continue
        ig = expected_information_gain(prior, test)
        value, cost, risk = (float(test.get(k, d)) for k, d in (("value", 1.0), ("cost", 0.0), ("risk", 0.0)))
        if not all(math.isfinite(x) and x >= 0 for x in (value, cost, risk)): raise ValueError("value, cost, risk must be finite and non-negative")
        ranked.append({"id": str(test.get("id", "")), "information_gain_bits": ig, "value": value, "cost": cost, "risk": risk, "utility": value * ig - cost_weight * cost - risk_weight * risk})
    return sorted(ranked, key=lambda row: (-row["utility"], -row["information_gain_bits"], row["id"]))

def retention_score(*, decision_value: float, reliability: float, novelty: float, age_seconds: float, half_life_seconds: float | None) -> float:
    """Current retrieval priority; age decay does not erase evidence or prove falsity."""
    vals = (decision_value, reliability, novelty, age_seconds)
    if any(not math.isfinite(x) or x < 0 for x in vals): raise ValueError("Inputs must be finite and non-negative")
    if reliability > 1 or novelty > 1: raise ValueError("reliability and novelty must be in [0, 1]")
    if half_life_seconds is None: decay = 1.0
    else:
        if not math.isfinite(half_life_seconds) or half_life_seconds <= 0: raise ValueError("half_life_seconds must be positive or None")
        decay = math.exp(-math.log(2) * age_seconds / half_life_seconds)
    return decision_value * reliability * novelty * decay

def rank_retention(items: Iterable[Mapping[str, Any]], *, now_seconds: float | None = None) -> list[dict[str, Any]]:
    """Rank hot-index priority. Identical hashes dedupe indexing only, never source retention."""
    now = time.time() if now_seconds is None else now_seconds
    if not math.isfinite(now): raise ValueError("now_seconds must be finite")
    rows = []
    for item in items:
        age = max(0.0, now - float(item["created_at_seconds"]))
        score = retention_score(decision_value=float(item.get("decision_value", 1.0)), reliability=float(item.get("reliability", .5)), novelty=float(item.get("novelty", 1.0)), age_seconds=age, half_life_seconds=item.get("half_life_seconds"))
        rows.append({"id": str(item["id"]), "content_hash": item.get("content_hash"), "age_seconds": age, "retention_score": score, "storage_bytes": max(0, int(item.get("storage_bytes", 0))), "action": "KEEP_RAW_AND_INDEX"})
    rows.sort(key=lambda row: (-row["retention_score"], row["id"]))
    by_hash = {}
    for row in rows:
        h = row["content_hash"]
        if isinstance(h, str) and h: by_hash.setdefault(h, []).append(row["id"])
    for row in rows:
        h = row["content_hash"]
        if isinstance(h, str) and h and len(by_hash[h]) > 1:
            row["duplicate_content_group"] = sorted(by_hash[h]); row["action"] = "KEEP_SOURCE_REFERENCE; DEDUPLICATE_INDEX_ONLY"
    return rows

class EventLedger:
    """Append-only SHA-256 chain using existing EVEZ event type names."""
    def __init__(self, events: Sequence[Mapping[str, Any]] | None = None):
        self.events = copy.deepcopy(list(events or []))
        valid, reason = self.verify()
        if not valid: raise ValueError(f"Invalid initial ledger: {reason}")
    @staticmethod
    def _hash_payload(event: Mapping[str, Any]) -> str:
        return canonical_hash({k: v for k, v in event.items() if k != "event_hash"})
    def append(self, event_type: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if event_type not in EVENT_TYPES: raise ValueError(f"Unsupported event type: {event_type}")
        previous = self.events[-1]["event_hash"] if self.events else "0" * 64
        event = {"sequence": len(self.events), "event_type": event_type, "previous_event_hash": previous, "payload": dict(payload)}
        event["event_hash"] = self._hash_payload(event); self.events.append(event)
        return dict(event)
    def verify(self) -> tuple[bool, str]:
        previous = "0" * 64
        for index, event in enumerate(self.events):
            if event.get("sequence") != index: return False, f"sequence mismatch at index {index}"
            if event.get("event_type") not in EVENT_TYPES: return False, f"unsupported event type at index {index}"
            if event.get("previous_event_hash") != previous: return False, f"previous hash mismatch at index {index}"
            expected = self._hash_payload(event)
            if event.get("event_hash") != expected: return False, f"event hash mismatch at index {index}"
            previous = expected
        return True, "ok"
    def replay(self) -> dict[str, Any]:
        valid, reason = self.verify()
        if not valid: raise ValueError(f"Cannot replay invalid ledger: {reason}")
        counts = {}; payloads = []
        for event in self.events:
            counts[event["event_type"]] = counts.get(event["event_type"], 0) + 1
            payloads.append({"sequence": event["sequence"], "event_type": event["event_type"], "payload": copy.deepcopy(event["payload"])})
        return {"event_count": len(self.events), "counts": dict(sorted(counts.items())), "committed_payloads": payloads, "head_hash": self.events[-1]["event_hash"] if self.events else "0" * 64}
