from __future__ import annotations

import json
import math
import random
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


try:
    from sentence_transformers import SentenceTransformer
except Exception:  # dependency can be optional in constrained environments
    SentenceTransformer = None


@dataclass
class Memory:
    memory_id: str
    content: str
    created_at: float
    tags: Dict[str, object] = field(default_factory=dict)
    confidence: float = 1.0
    embedding: Optional[List[float]] = None


class EmbeddingBackend:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model = SentenceTransformer(model_name) if SentenceTransformer else None

    def encode(self, texts: Sequence[str]) -> List[List[float]]:
        if self.model is not None:
            return [list(vec) for vec in self.model.encode(list(texts), normalize_embeddings=True)]
        return [self._hash_embed(t) for t in texts]

    @staticmethod
    def _hash_embed(text: str, dims: int = 32) -> List[float]:
        vec = [0.0] * dims
        for idx, ch in enumerate(text.lower()):
            vec[idx % dims] += (ord(ch) % 31) / 31.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b:
        return 0.0
    n = min(len(a), len(b))
    dot = sum(a[i] * b[i] for i in range(n))
    na = math.sqrt(sum(a[i] * a[i] for i in range(n))) or 1.0
    nb = math.sqrt(sum(b[i] * b[i] for i in range(n))) or 1.0
    return dot / (na * nb)


class DreamEngine:
    def __init__(self, journal_path: str = "agents/dream/dream_journal.jsonl", embedding_backend: Optional[EmbeddingBackend] = None) -> None:
        self.embedding_backend = embedding_backend or EmbeddingBackend()
        self.journal_path = Path(journal_path)
        self.coactivation_pairs: Set[Tuple[str, str]] = set()

    @staticmethod
    def should_enter_dream_mode(cpu_samples: Sequence[float], threshold: float = 20.0, duration_s: int = 60) -> bool:
        if len(cpu_samples) < duration_s:
            return False
        window = cpu_samples[-duration_s:]
        return all(sample < threshold for sample in window)

    def run_dream_session(self, episodic_memories: Sequence[Memory], max_replay: int = 1000) -> Dict[str, object]:
        start = time.time()
        session_id = f"dream-{uuid.uuid4()}"
        replay = list(episodic_memories[-max_replay:])
        random.shuffle(replay)
        self._ensure_embeddings(replay)

        insights: List[Memory] = []
        for i in range(len(replay)):
            for j in range(i + 1, len(replay)):
                a, b = replay[i], replay[j]
                pair = tuple(sorted((a.memory_id, b.memory_id)))
                if pair in self.coactivation_pairs:
                    continue
                sim = cosine_similarity(a.embedding or [], b.embedding or [])
                if 0.3 <= sim <= 0.6:
                    insight = Memory(
                        memory_id=f"insight-{uuid.uuid4()}",
                        content=f"Dream bridge: '{a.content[:80]}' ↔ '{b.content[:80]}'",
                        created_at=time.time(),
                        tags={
                            "dream_origin": True,
                            "source_memories": [a.memory_id, b.memory_id],
                            "similarity": round(sim, 4),
                        },
                        confidence=0.6,
                    )
                    insight.embedding = self.embedding_backend.encode([insight.content])[0]
                    insights.append(insight)
                    self.coactivation_pairs.add(pair)

        duration_s = round(time.time() - start, 3)
        session = {
            "session_id": session_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start)),
            "memories_replayed": len(replay),
            "insights_generated": len(insights),
            "duration_s": duration_s,
        }
        self._append_journal(session)
        return {"session": session, "insights": insights}

    def _append_journal(self, item: Dict[str, object]) -> None:
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        with self.journal_path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(item, ensure_ascii=False) + "\n")

    def _ensure_embeddings(self, memories: Iterable[Memory]) -> None:
        pending = [m for m in memories if m.embedding is None]
        if not pending:
            return
        vectors = self.embedding_backend.encode([m.content for m in pending])
        for memory, vec in zip(pending, vectors):
            memory.embedding = vec
