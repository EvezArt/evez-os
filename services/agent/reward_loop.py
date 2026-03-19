import json
import math
import os
import sqlite3
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class RewardVector:
    code_quality: float
    test_coverage: float
    system_uptime: float
    self_expansion_rate: float

    @property
    def total(self) -> float:
        return self.code_quality + self.test_coverage + self.system_uptime + self.self_expansion_rate


class EvezBrainRewardLoop:
    """Autonomous reward loop with SQLite persistence and decision biasing."""

    def __init__(self, db_path: str | None = None):
        default_path = Path(__file__).resolve().parents[2] / "artifacts" / "evezbrain_reward_ledger.sqlite3"
        self.db_path = db_path or os.getenv("EVEZ_REWARD_LEDGER", str(default_path))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reward_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL NOT NULL,
                    action_type TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    metadata_json TEXT NOT NULL,
                    code_quality REAL NOT NULL,
                    test_coverage REAL NOT NULL,
                    system_uptime REAL NOT NULL,
                    self_expansion_rate REAL NOT NULL,
                    total_reward REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_reward_events_action_ts
                ON reward_events(action_type, ts)
                """
            )

    def score_action(self, action_type: str, success: bool, metadata: Dict[str, Any]) -> RewardVector:
        quality = 0.1 if success else -0.4
        coverage = 0.0
        uptime = 0.05 if success else -0.2
        expansion = 0.0

        if action_type == "file_write":
            lint_clean = bool(metadata.get("lint_clean", False))
            quality += 0.35 if lint_clean else 0.1
            tests_touched = float(metadata.get("tests_touched", 0))
            coverage += min(0.25, tests_touched * 0.05)
        elif action_type == "api_call":
            latency_ms = float(metadata.get("latency_ms", 0.0))
            status_code = int(metadata.get("status_code", 200 if success else 500))
            uptime += 0.25 if 200 <= status_code < 500 else -0.4
            uptime += max(-0.2, (250.0 - latency_ms) / 2000.0)
        elif action_type == "test_result":
            passed = bool(metadata.get("passed", success))
            num_tests = max(1, int(metadata.get("num_tests", 1)))
            coverage += (0.4 if passed else -0.5) + min(0.35, num_tests * 0.01)
            quality += 0.2 if passed else -0.35
        elif action_type == "pr_merge":
            review_score = float(metadata.get("review_score", 0.0))
            quality += min(0.6, max(-0.3, review_score))
            expansion += 0.45 if success else -0.25
            coverage += 0.15 if metadata.get("tests_green", False) else -0.2
        else:
            # Generalized autonomous actions can still earn expansion rewards.
            novelty = float(metadata.get("novelty", 0.0))
            expansion += max(-0.1, min(0.3, novelty))

        if metadata.get("expanded_capability"):
            expansion += 0.35
        if metadata.get("rollback"):
            quality -= 0.4
            uptime -= 0.2

        return RewardVector(
            code_quality=round(quality, 4),
            test_coverage=round(coverage, 4),
            system_uptime=round(uptime, 4),
            self_expansion_rate=round(expansion, 4),
        )

    def record_action(self, action_type: str, success: bool, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        metadata = metadata or {}
        reward = self.score_action(action_type=action_type, success=success, metadata=metadata)
        now = time.time()

        with self._lock:
            with self._connect() as conn:
                cur = conn.execute(
                    """
                    INSERT INTO reward_events(
                        ts, action_type, success, metadata_json,
                        code_quality, test_coverage, system_uptime, self_expansion_rate, total_reward
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        now,
                        action_type,
                        int(success),
                        json.dumps(metadata, sort_keys=True),
                        reward.code_quality,
                        reward.test_coverage,
                        reward.system_uptime,
                        reward.self_expansion_rate,
                        reward.total,
                    ),
                )
                event_id = cur.lastrowid

        return {
            "event_id": event_id,
            "action_type": action_type,
            "success": success,
            "reward": {
                "code_quality": reward.code_quality,
                "test_coverage": reward.test_coverage,
                "system_uptime": reward.system_uptime,
                "self_expansion_rate": reward.self_expansion_rate,
                "total": reward.total,
            },
        }

    def decision_profile(self, candidates: Iterable[str] | None = None, lookback: int = 500) -> Dict[str, Any]:
        candidates = list(candidates or ["file_write", "api_call", "test_result", "pr_merge"])

        with self._connect() as conn:
            totals = conn.execute(
                """
                SELECT
                    COALESCE(AVG(code_quality), 0.0) AS code_quality,
                    COALESCE(AVG(test_coverage), 0.0) AS test_coverage,
                    COALESCE(AVG(system_uptime), 0.0) AS system_uptime,
                    COALESCE(AVG(self_expansion_rate), 0.0) AS self_expansion_rate,
                    COALESCE(COUNT(*), 0) AS n
                FROM (
                    SELECT * FROM reward_events ORDER BY id DESC LIMIT ?
                )
                """,
                (lookback,),
            ).fetchone()

            action_scores: List[Dict[str, Any]] = []
            for action in candidates:
                row = conn.execute(
                    """
                    SELECT
                        COALESCE(AVG(total_reward), 0.0) AS avg_reward,
                        COALESCE(AVG(success), 0.0) AS success_rate,
                        COALESCE(COUNT(*), 0) AS n
                    FROM (
                        SELECT * FROM reward_events WHERE action_type = ? ORDER BY id DESC LIMIT ?
                    )
                    """,
                    (action, lookback),
                ).fetchone()
                exploitation = float(row["avg_reward"])
                exploration_boost = 0.2 / (1.0 + float(row["n"]))
                utility = exploitation + exploration_boost
                action_scores.append(
                    {
                        "action": action,
                        "avg_reward": round(exploitation, 4),
                        "success_rate": round(float(row["success_rate"]), 4),
                        "samples": int(row["n"]),
                        "utility": round(utility, 4),
                    }
                )

        denom = sum(math.exp(item["utility"]) for item in action_scores) or 1.0
        for item in action_scores:
            item["probability"] = round(math.exp(item["utility"]) / denom, 4)
        action_scores.sort(key=lambda item: item["probability"], reverse=True)

        objectives = {
            "code_quality": round(float(totals["code_quality"]), 4),
            "test_coverage": round(float(totals["test_coverage"]), 4),
            "system_uptime": round(float(totals["system_uptime"]), 4),
            "self_expansion_rate": round(float(totals["self_expansion_rate"]), 4),
        }

        return {
            "ledger": self.db_path,
            "events_sampled": int(totals["n"]),
            "objective_means": objectives,
            "recommended_action": action_scores[0]["action"] if action_scores else None,
            "action_policy": action_scores,
        }
