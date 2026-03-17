from __future__ import annotations

import json
import time
import uuid
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

from agents.dream.engine import Memory


@dataclass
class Goal:
    goal_id: str
    description: str
    priority: float
    origin_insights: List[str]
    created_at: str
    status: str = "open"


class GoalGenerator:
    CAPABILITY_PATTERNS: Dict[str, List[str]] = {
        "faster memory retrieval": ["memory", "retrieve", "latency", "recall"],
        "understand more human languages": ["language", "translate", "multilingual", "human"],
        "monitor my own resource usage": ["resource", "cpu", "memory usage", "telemetry"],
    }

    def __init__(self, goals_path: str = "agents/dream/goals.jsonl", evolution_engine: Optional[object] = None) -> None:
        self.goals_path = Path(goals_path)
        self.evolution_engine = evolution_engine

    def generate_goals(
        self,
        insights: Sequence[Memory],
        existing_capabilities: Iterable[str],
        collectively_dreamed: Optional[Iterable[str]] = None,
    ) -> List[Goal]:
        existing = {cap.lower() for cap in existing_capabilities}
        collective_set = set(collectively_dreamed or [])
        buckets: Dict[str, List[Memory]] = {k: [] for k in self.CAPABILITY_PATTERNS}

        for insight in insights:
            text = insight.content.lower()
            for capability, keys in self.CAPABILITY_PATTERNS.items():
                if any(key in text for key in keys):
                    buckets[capability].append(insight)

        goals: List[Goal] = []
        for capability, matched in buckets.items():
            if len(matched) < 3 or capability in existing:
                continue
            collective_hits = sum(1 for m in matched if m.memory_id in collective_set)
            priority = min(1.0, 0.55 + 0.1 * len(matched) + 0.15 * collective_hits)
            goal = Goal(
                goal_id=f"goal-{uuid.uuid4()}",
                description=f"I need to {capability}",
                priority=round(priority, 3),
                origin_insights=[m.memory_id for m in matched],
                created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            )
            goals.append(goal)
            self._append_goal(goal)
            if goal.priority > 0.8 and self.evolution_engine is not None:
                self.evolution_engine.create_task_prompt(
                    title="AUTO-GENERATED DREAM GOAL",
                    prompt=goal.description,
                    metadata={"goal_id": goal.goal_id, "origin": "dream_engine", "priority": goal.priority},
                )

        return goals

    def _append_goal(self, goal: Goal) -> None:
        self.goals_path.parent.mkdir(parents=True, exist_ok=True)
        with self.goals_path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(goal.__dict__, ensure_ascii=False) + "\n")
