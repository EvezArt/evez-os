from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Sequence

from agents.dream.engine import Memory, cosine_similarity


@dataclass
class DreamShareMessage:
    msg_type: str
    sender_id: str
    insight_ids: List[str]
    insights: List[dict]


class DreamSharer:
    def __init__(self, node_id: str, novelty_threshold: float = 0.82) -> None:
        self.node_id = node_id
        self.novelty_threshold = novelty_threshold
        self.collective_counter: Counter[str] = Counter()

    def package_top_insights(self, insights: Sequence[Memory], top_n: int = 5) -> DreamShareMessage:
        top = sorted(insights, key=lambda i: i.confidence, reverse=True)[:top_n]
        return DreamShareMessage(
            msg_type="DREAM_SHARE",
            sender_id=self.node_id,
            insight_ids=[i.memory_id for i in top],
            insights=[
                {
                    "memory_id": i.memory_id,
                    "content": i.content,
                    "confidence": i.confidence,
                    "embedding": i.embedding,
                    "tags": i.tags,
                }
                for i in top
            ],
        )

    def broadcast(self, message: DreamShareMessage, peers: Iterable[Callable[[DreamShareMessage], None]]) -> None:
        for peer in peers:
            peer(message)

    def receive(self, message: DreamShareMessage, own_memories: Sequence[Memory]) -> Dict[str, List[Memory]]:
        absorbed: List[Memory] = []
        collective: List[Memory] = []
        own_embeddings = [m.embedding or [] for m in own_memories]

        for raw in message.insights:
            candidate = Memory(
                memory_id=raw["memory_id"],
                content=raw["content"],
                created_at=0.0,
                tags=dict(raw.get("tags") or {}),
                confidence=float(raw.get("confidence", 0.6)),
                embedding=raw.get("embedding"),
            )
            if self._is_novel(candidate, own_embeddings):
                absorbed.append(candidate)
                key = self._signature(candidate)
                self.collective_counter[key] += 1
                if self.collective_counter[key] >= 3:
                    candidate.tags["collectively_dreamed"] = True
                    candidate.tags["priority"] = 1.0
                    collective.append(candidate)

        return {"absorbed": absorbed, "collective": collective}

    def _is_novel(self, candidate: Memory, own_embeddings: Sequence[Sequence[float]]) -> bool:
        if not candidate.embedding:
            return True
        for emb in own_embeddings:
            if emb and cosine_similarity(candidate.embedding, emb) >= self.novelty_threshold:
                return False
        return True

    @staticmethod
    def _signature(memory: Memory) -> str:
        return memory.content.lower().strip()[:120]
