"""Sequential research controller with evidence-bound, bounded self-funding.

A holdout is committed before its outcomes are supplied. The controller rejects
reuse of evaluation cohorts, spends a family-wise alpha budget across reserved
trials, debits costs before a test proceeds, awards credit only for positive
held-out improvement after cost, caps per-trial and lifetime credits, and records
reservations and settlements with existing CHECKPOINT_ISSUED ledger events.

This mechanism cannot prove caller-supplied provenance flags truthful. An
independent verifier must validate source lineage.
"""
from __future__ import annotations

import fcntl
import math
import os
import re
import time
from contextlib import contextmanager
from typing import Any, Mapping, Sequence

from .kernel import canonical_hash
from .research import aggregate_research_reward, _strict_forecast_distribution
from .store import JsonlLedgerStore

CONTROLLER_ID = "evez.epie.research-controller.v1"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _finite_nonnegative(name: str, value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number, not a boolean")
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return result


def _normalized_forecast_records(
    records: Sequence[Mapping[str, Any]], *, outcomes_allowed: bool
) -> tuple[list[dict[str, Any]], str, str]:
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes)) or not records:
        raise ValueError("forecast records must be a non-empty sequence")
    identities = []
    forecasts = []
    seen_ids = set()
    seen_units = set()
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise ValueError(f"forecast record {index} must be an object")
        if not outcomes_allowed and "observed_outcome" in record:
            raise ValueError("Reserve must commit forecasts before observed outcomes are supplied")
        sample_id = record.get("id")
        unit = record.get("independence_key")
        if not isinstance(sample_id, str) or not sample_id:
            raise ValueError(f"record {index} requires a non-empty id")
        if sample_id in seen_ids:
            raise ValueError(f"duplicate evaluation id: {sample_id}")
        seen_ids.add(sample_id)
        if not isinstance(unit, str) or not unit:
            raise ValueError(f"record {sample_id} requires an independence_key")
        if unit in seen_units:
            raise ValueError(f"repeated independence_key: {unit}")
        seen_units.add(unit)
        baseline = _strict_forecast_distribution(record.get("baseline_forecast"))
        updated = _strict_forecast_distribution(record.get("updated_forecast"))
        if set(baseline) != set(updated):
            raise ValueError(f"{sample_id}: baseline and updated outcome spaces differ")
        identities.append({"id": sample_id, "independence_key": unit})
        forecasts.append({
            "id": sample_id,
            "baseline_forecast": baseline,
            "updated_forecast": updated,
        })
    identities.sort(key=lambda row: row["id"])
    forecasts.sort(key=lambda row: row["id"])
    cohort_hash = canonical_hash(identities)
    forecast_hash = canonical_hash(forecasts)
    return forecasts, cohort_hash, forecast_hash


class ResearchExperimentController:
    """Process-serialized experimental budget and research-credit ledger.

    Trial t receives alpha_t = family_alpha / (t * (t + 1)); the infinite sum
    equals family_alpha. Reserving a trial consumes its alpha slot even if it is
    later abandoned. This makes repeated adaptive looks progressively stricter.

    Initial budget, search costs, risk costs, and credits share one utility unit.
    Earned credit may replenish spending through credit_rate, but total lifetime
    and per-trial credit are hard-capped.
    """

    def __init__(
        self,
        store: JsonlLedgerStore,
        *,
        budget_id: str,
        initial_budget: float,
        max_total_credit: float,
        max_credit_per_trial: float,
        family_alpha: float = 0.05,
        credit_rate: float = 1.0,
        min_cases: int = 30,
    ):
        if not isinstance(budget_id, str) or not budget_id.strip():
            raise ValueError("budget_id must be a non-empty stable identifier")
        self.store = store
        self.budget_id = budget_id
        self.initial_budget = _finite_nonnegative("initial_budget", initial_budget)
        self.max_total_credit = _finite_nonnegative("max_total_credit", max_total_credit)
        self.max_credit_per_trial = _finite_nonnegative("max_credit_per_trial", max_credit_per_trial)
        self.credit_rate = _finite_nonnegative("credit_rate", credit_rate)
        if isinstance(family_alpha, bool) or not isinstance(family_alpha, (int, float)) or not math.isfinite(family_alpha) or not 0 < family_alpha < 1:
            raise ValueError("family_alpha must be finite and strictly between 0 and 1")
        self.family_alpha = float(family_alpha)
        if isinstance(min_cases, bool) or not isinstance(min_cases, int) or min_cases < 2:
            raise ValueError("min_cases must be an integer >= 2")
        self.min_cases = min_cases
        self.policy = {
            "initial_budget": self.initial_budget,
            "max_total_credit": self.max_total_credit,
            "max_credit_per_trial": self.max_credit_per_trial,
            "family_alpha": self.family_alpha,
            "credit_rate": self.credit_rate,
            "min_cases": self.min_cases,
        }
        self.policy_hash = canonical_hash(self.policy)
        self.lock_path = self.store.path.with_name(self.store.path.name + ".research.lock")

    @contextmanager
    def _lock(self):
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(str(self.lock_path), flags, 0o600)
        try:
            if not os.path.isfile(self.lock_path):
                raise ValueError("Research lock path must be a regular file")
            os.fchmod(fd, 0o600)
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)

    @staticmethod
    def _payload(event: Mapping[str, Any]) -> Mapping[str, Any]:
        payload = event.get("payload", {})
        return payload if isinstance(payload, Mapping) else {}

    def _read_scoped(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        ledger = self.store.load()
        scoped = [
            dict(event) for event in ledger.events
            if self._payload(event).get("controller") == CONTROLLER_ID
            and self._payload(event).get("budget_id") == self.budget_id
        ]
        openings = [self._payload(e) for e in scoped if self._payload(e).get("kind") == "BUDGET_OPENED"]
        if not openings:
            self.store.append("CHECKPOINT_ISSUED", {
                "controller": CONTROLLER_ID,
                "budget_id": self.budget_id,
                "kind": "BUDGET_OPENED",
                "policy": self.policy,
                "policy_hash": self.policy_hash,
                "created_at_unix": time.time(),
            })
            ledger = self.store.load()
            scoped = [
                dict(event) for event in ledger.events
                if self._payload(event).get("controller") == CONTROLLER_ID
                and self._payload(event).get("budget_id") == self.budget_id
            ]
            openings = [self._payload(e) for e in scoped if self._payload(e).get("kind") == "BUDGET_OPENED"]
        if len(openings) != 1:
            raise ValueError("Research budget must have exactly one opening receipt")
        opening = openings[0]
        if opening.get("policy_hash") != self.policy_hash or opening.get("policy") != self.policy:
            raise ValueError("Research budget policy mismatch; opening budget is immutable")
        return scoped, opening

    @staticmethod
    def _reservations(scoped: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
        return [ResearchExperimentController._payload(e) for e in scoped
                if ResearchExperimentController._payload(e).get("kind") == "TRIAL_RESERVED"]

    @staticmethod
    def _settlements(scoped: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
        return [ResearchExperimentController._payload(e) for e in scoped
                if ResearchExperimentController._payload(e).get("kind") == "TRIAL_SETTLED"]

    def _status_from(self, scoped: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        reservations = self._reservations(scoped)
        settlements = self._settlements(scoped)
        spent = math.fsum(float(r["search_cost"]) + float(r["risk_cost"]) for r in reservations)
        credits = math.fsum(float(s["credit_issued"]) for s in settlements)
        remaining = self.initial_budget + self.credit_rate * credits - spent
        return {
            "budget_id": self.budget_id,
            "initial_budget": self.initial_budget,
            "total_spent": spent,
            "total_credit_issued": credits,
            "remaining_budget": remaining,
            "credit_pool_remaining": max(0.0, self.max_total_credit - credits),
            "reserved_trials": len(reservations),
            "settled_trials": len(settlements),
            "alpha_spent": math.fsum(float(r["alpha_spending"]) for r in reservations),
            "family_alpha": self.family_alpha,
            "status": "BUDGET_AVAILABLE" if remaining > 0 else "BUDGET_EXHAUSTED",
        }

    def status(self) -> dict[str, Any]:
        with self._lock():
            scoped, _ = self._read_scoped()
            return self._status_from(scoped)

    def reserve(
        self,
        *,
        trial_id: str,
        forecast_records: Sequence[Mapping[str, Any]],
        search_cost: float,
        risk_cost: float,
    ) -> dict[str, Any]:
        """Commit forecasts and debit cost before outcomes are supplied."""
        if not isinstance(trial_id, str) or not trial_id.strip():
            raise ValueError("trial_id must be a non-empty stable identifier")
        cost = _finite_nonnegative("search_cost", search_cost)
        risk = _finite_nonnegative("risk_cost", risk_cost)
        normalized, cohort_hash, forecast_hash = _normalized_forecast_records(forecast_records, outcomes_allowed=False)
        with self._lock():
            scoped, _ = self._read_scoped()
            reservations = self._reservations(scoped)
            existing = next((r for r in reservations if r.get("trial_id") == trial_id), None)
            if existing is not None:
                expected = (existing.get("cohort_hash"), existing.get("forecast_hash"),
                            float(existing.get("search_cost", -1)), float(existing.get("risk_cost", -1)))
                proposed = (cohort_hash, forecast_hash, cost, risk)
                if expected != proposed:
                    raise ValueError("trial_id already reserved with different inputs")
                settled = any(s.get("trial_id") == trial_id for s in self._settlements(scoped))
                return {
                    "decision": "ALREADY_SETTLED" if settled else "ALREADY_RESERVED",
                    "reservation": dict(existing),
                    "status": self._status_from(scoped),
                }
            if any(r.get("cohort_hash") == cohort_hash for r in reservations):
                raise ValueError("Evaluation cohort already used by another trial; reserve a new held-out cohort")
            status = self._status_from(scoped)
            requested = cost + risk
            if requested > status["remaining_budget"]:
                return {
                    "decision": "STOP",
                    "reason": "BUDGET_EXHAUSTED",
                    "requested_budget": requested,
                    "status": status,
                }
            trial_index = len(reservations) + 1
            alpha_spending = self.family_alpha / (trial_index * (trial_index + 1))
            event = self.store.append("CHECKPOINT_ISSUED", {
                "controller": CONTROLLER_ID,
                "budget_id": self.budget_id,
                "kind": "TRIAL_RESERVED",
                "trial_id": trial_id,
                "trial_index": trial_index,
                "cohort_hash": cohort_hash,
                "forecast_hash": forecast_hash,
                "search_cost": cost,
                "risk_cost": risk,
                "alpha_spending": alpha_spending,
                "reserved_at_unix": time.time(),
            })
            return {
                "decision": "RESERVED",
                "reservation": self._payload(event),
                "status": self._status_from(scoped + [event]),
            }

    def settle(self, *, trial_id: str, samples: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        """Evaluate committed forecasts once outcomes arrive; retry safely."""
        if not isinstance(trial_id, str) or not trial_id.strip():
            raise ValueError("trial_id must be a non-empty stable identifier")
        if not isinstance(samples, Sequence) or isinstance(samples, (str, bytes)):
            raise ValueError("samples must be a sequence of evaluation records")
        evaluation_hash = canonical_hash(sorted((dict(s) for s in samples), key=lambda s: str(s.get("id", ""))))
        with self._lock():
            scoped, _ = self._read_scoped()
            reservations = self._reservations(scoped)
            reservation = next((r for r in reservations if r.get("trial_id") == trial_id), None)
            if reservation is None:
                raise ValueError("No reservation found for trial_id")
            existing = next((s for s in self._settlements(scoped) if s.get("trial_id") == trial_id), None)
            if existing is not None:
                if existing.get("evaluation_hash") != evaluation_hash:
                    raise ValueError("trial_id already settled with different evaluation inputs")
                return {"decision": "ALREADY_SETTLED", "settlement": dict(existing), "status": self._status_from(scoped)}

            normalized, cohort_hash, forecast_hash = _normalized_forecast_records(samples, outcomes_allowed=True)
            if cohort_hash != reservation.get("cohort_hash"):
                raise ValueError("Settled samples do not match the reserved evaluation cohort")
            if forecast_hash != reservation.get("forecast_hash"):
                raise ValueError("Settled forecasts differ from the pre-outcome prediction commitment")
            for sample in samples:
                if "observed_outcome" not in sample:
                    raise ValueError(f"Sample {sample.get('id')} lacks observed_outcome")

            result = aggregate_research_reward(
                samples,
                search_cost=float(reservation["search_cost"]),
                risk_cost=float(reservation["risk_cost"]),
                projected_future_cases=1.0,
                score_weight=1.0,
                min_cases=self.min_cases,
                alpha=float(reservation["alpha_spending"]),
            )
            lower_bound = result.get("lower_confidence_bound")
            pool_remaining = self._status_from(scoped)["credit_pool_remaining"]
            credit = 0.0
            status = result.get("status", "NO_REWARD")
            if result.get("eligible") is True and isinstance(lower_bound, (int, float)) and lower_bound > 0 and pool_remaining > 0:
                credit = min(float(lower_bound), self.max_credit_per_trial, pool_remaining)
                if credit <= float(reservation["search_cost"]) + float(reservation["risk_cost"]):
                    credit = 0.0
                    status = "NO_REWARD_NET_VALUE_NOT_POSITIVE"
                else:
                    status = "REWARD_SUPPORTED"
            elif result.get("eligible") is True and lower_bound is not None and lower_bound <= 0:
                status = "NO_REWARD_GAIN_NOT_PROVEN"
            elif result.get("eligible") is True and pool_remaining <= 0:
                status = "NO_REWARD_CREDIT_POOL_EXHAUSTED"

            expenditure = float(reservation["search_cost"]) + float(reservation["risk_cost"])
            net_reward = credit - expenditure
            status_after = self._status_from(scoped)
            total_credit_after = status_after["total_credit_issued"] + credit
            total_spent_after = status_after["total_spent"]
            remaining_after = self.initial_budget + self.credit_rate * total_credit_after - total_spent_after
            event = self.store.append("CHECKPOINT_ISSUED", {
                "controller": CONTROLLER_ID,
                "budget_id": self.budget_id,
                "kind": "TRIAL_SETTLED",
                "trial_id": trial_id,
                "cohort_hash": cohort_hash,
                "evaluation_hash": evaluation_hash,
                "result": result,
                "status": status,
                "credit_issued": credit,
                "net_reward": net_reward,
                "remaining_budget_after": remaining_after,
                "settled_at_unix": time.time(),
            })
            return {
                "decision": status,
                "settlement": dict(self._payload(event)),
                "status": self._status_from(scoped + [event]),
            }
