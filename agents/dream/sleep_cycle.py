from __future__ import annotations

import time
from typing import Dict, List, Sequence

from agents.dream.engine import DreamEngine, Memory


class SleepCycleManager:
    def __init__(self, dream_engine: DreamEngine, activity_minutes: int = 90, dream_minutes: int = 15) -> None:
        self.dream_engine = dream_engine
        self.activity_s = activity_minutes * 60
        self.dream_s = dream_minutes * 60
        self.cycle_s = self.activity_s + self.dream_s

    def phase_at(self, timestamp_s: float) -> str:
        offset = int(timestamp_s) % self.cycle_s
        return "activity" if offset < self.activity_s else "dream"

    def run_dream_phase(self, episodic_memories: Sequence[Memory], learned_context: Sequence[Memory]) -> Dict[str, object]:
        consolidated = self.consolidate_memories(episodic_memories, learned_context)
        session = self.dream_engine.run_dream_session(consolidated)
        return {"consolidated": consolidated, **session}

    def consolidate_memories(self, episodic_memories: Sequence[Memory], learned_context: Sequence[Memory]) -> List[Memory]:
        recent = list(episodic_memories[-(90 * 60) :])
        if not recent:
            return []
        self.dream_engine._ensure_embeddings(recent)
        if learned_context:
            self.dream_engine._ensure_embeddings(learned_context)
            avg = [0.0] * len((learned_context[0].embedding or [0.0]))
            for m in learned_context:
                emb = m.embedding or []
                for i, val in enumerate(emb):
                    avg[i] += val
            denom = max(1, len(learned_context))
            avg = [v / denom for v in avg]
            for memory in recent:
                if not memory.embedding:
                    continue
                memory.embedding = [(memory.embedding[i] * 0.7) + (avg[i] * 0.3) for i in range(len(avg))]
        for memory in recent:
            memory.tags["consolidated"] = True
        return recent
