#!/usr/bin/env python3
"""
Unified Memory Store - EVEZ-style persistent memory with decay
Provides semantic search and context injection for agent systems
"""

import json
import time
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid
import re

@dataclass
class Memory:
    id: str
    content: str
    timestamp: float
    importance: float  # 0-1, auto-calculated
    decay_rate: float  # per cycle
    tags: List[str]
    context: Dict[str, Any]  # source, type, etc.
    hash: str

class UnifiedMemory:
    """EVEZ-style memory with semantic retrieval and decay"""
    
    def __init__(self, path: str = "./memory.jsonl", decay_rate: float = 0.98):
        self.path = path
        self.decay_rate = decay_rate
        self.memories: List[Memory] = []
        self._load()
    
    def _load(self):
        try:
            with open(self.path, "r") as f:
                for line in f:
                    m = json.loads(line)
                    self.memories.append(Memory(**m))
        except FileNotFoundError:
            pass
    
    def _save(self, memory: Memory):
        with open(self.path, "a") as f:
            f.write(json.dumps(asdict(memory)) + "\n")
    
    def _compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _calc_importance(self, content: str, context: Dict) -> float:
        """Calculate importance based on content and context"""
        base = 0.5
        # Length bonus
        if len(content) > 200:
            base += 0.1
        # Source priority
        if context.get("source") in ["agent", "decision", "success"]:
            base += 0.2
        if context.get("type") == "critical":
            base += 0.3
        return min(1.0, base)
    
    def store(self, content: str, tags: Optional[List[str]] = None, 
              context: Optional[Dict] = None) -> Memory:
        """Store new memory"""
        memory = Memory(
            id=str(uuid.uuid4()),
            content=content,
            timestamp=time.time(),
            importance=self._calc_importance(content, context or {}),
            decay_rate=self.decay_rate,
            tags=tags or [],
            context=context or {},
            hash=self._compute_hash(content)
        )
        self.memories.append(memory)
        self._save(memory)
        return memory
    
    def search(self, query: str, limit: int = 5) -> List[Memory]:
        """Semantic(ish) search - keyword + importance weighted"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored = []
        for m in self.memories:
            # Skip decayed memories
            effective_importance = m.importance * (self.decay_rate ** ((time.time() - m.timestamp) / 3600))
            if effective_importance < 0.1:
                continue
            
            # Keyword match
            content_lower = m.content.lower()
            matches = sum(1 for w in query_words if w in content_lower)
            
            # Tag match bonus
            tag_matches = sum(1 for t in m.tags if t.lower() in query_lower)
            
            score = (matches * 0.3 + tag_matches * 0.5) * effective_importance
            if score > 0:
                scored.append((score, m))
        
        scored.sort(reverse=True)
        return [m for _, m in scored[:limit]]
    
    def get_context(self, query: str, max_tokens: int = 2000) -> str:
        """Get context string for injection"""
        results = self.search(query)
        if not results:
            return ""
        
        context_parts = ["[MEMORY CONTEXT]"]
        for m in results:
            age = (time.time() - m.timestamp) / 3600
            context_parts.append(f"- [{m.tags[0] if m.tags else 'memory'} | {age:.1f}h ago] {m.content[:200]}")
        
        return "\n".join(context_parts[:10])
    
    def decay(self) -> int:
        """Apply decay to all memories, return count removed"""
        before = len(self.memories)
        self.memories = [
            m for m in self.memories
            if m.importance * (self.decay_rate ** ((time.time() - m.timestamp) / 3600)) >= 0.1
        ]
        return before - len(self.memories)
    
    def get_stats(self) -> Dict:
        return {
            "total_memories": len(self.memories),
            "avg_importance": sum(m.importance for m in self.memories) / max(1, len(self.memories)),
            "tags": list(set(t for m in self.memories for t in m.tags)),
            "oldest": min((m.timestamp for m in self.memories), default=0),
            "newest": max((m.timestamp for m in self.memories), default=0)
        }


# CLI
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Unified Memory")
    parser.add_argument("command", choices=["store", "search", "decay", "stats"])
    parser.add_argument("--content", "-c", help="Memory content")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--tags", "-t", help="Comma-separated tags")
    parser.add_argument("--path", "-p", default="./memory.jsonl")
    args = parser.parse_args()
    
    memory = UnifiedMemory(args.path)
    
    if args.command == "store":
        tags = args.tags.split(",") if args.tags else []
        m = memory.store(args.content or " ", tags=tags)
        print(f"Stored: {m.id[:8]}")
    elif args.command == "search":
        results = memory.search(args.query or "")
        for r in results:
            print(f"[{r.id[:8]}] {r.content[:100]}...")
    elif args.command == "decay":
        print(f"Removed: {memory.decay()} memories")
    elif args.command == "stats":
        print(json.dumps(memory.get_stats(), indent=2))