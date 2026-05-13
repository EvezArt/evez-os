#!/usr/bin/env python3
"""
memory_system.py - EVEZ-OS Memory Architecture
Episodic, Working, and Long-term Memory with consolidation
"""
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class MemoryType(Enum):
    EPISODIC = "episodic"
    WORKING = "working"
    LONG_TERM = "long_term"
    PROCEDURAL = "procedural"

@dataclass
class MemoryItem:
    content: str
    type: MemoryType
    importance: float
    timestamp: float
    tags: List[str]
    embeddings: Optional[List[float]] = None
    consolidated_from: List[str] = None
    
    def __post_init__(self):
        if self.consolidated_from is None:
            self.consolidated_from = []

class MemorySystem:
    def __init__(self, state_dir: str = "/root/.openclaw/workspace/evez-os/live/memory"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Memory stores
        self.episodic: List[MemoryItem] = []
        self.working: Dict[str, MemoryItem] = {}
        self.long_term: List[MemoryItem] = []
        self.procedural: Dict[str, MemoryItem] = {}
        
        self.spine_path = self.state_dir / "memory_spine.jsonl"
        self._load()
        
    def record(self, content: str, memory_type: MemoryType = MemoryType.EPISODIC,
               importance: float = 0.5, tags: List[str] = None) -> str:
        """Record a memory item"""
        item = MemoryItem(
            content=content,
            type=memory_type,
            importance=importance,
            timestamp=time.time(),
            tags=tags or []
        )
        
        if memory_type == MemoryType.EPISODIC:
            self.episodic.append(item)
        elif memory_type == MemoryType.WORKING:
            key = f"w_{len(self.working)}"
            self.working[key] = item
        elif memory_type == MemoryType.LONG_TERM:
            self.long_term.append(item)
        elif memory_type == MemoryType.PROCEDURAL:
            key = f"proc_{len(self.procedural)}"
            self.procedural[key] = item
            
        self._log_to_spine("record", {"id": id(item), "content": content[:80]})
        self._save()
        return str(id(item))
        
    def consolidate(self, threshold: float = 0.7):
        """Consolidate important episodic memories to long-term"""
        consolidated = []
        for item in self.episodic:
            if item.importance >= threshold or self._semantic_overlap(item):
                self.long_term.append(item)
                item.consolidated_from = [str(id(item))]
                consolidated.append(item.content[:60])
                
        self.episodic = self.episodic[-100:]
        self._log_to_spine("consolidate", {"count": len(consolidated)})
        return consolidated
        
    def _semantic_overlap(self, item: MemoryItem) -> bool:
        for existing in self.long_term:
            if item.content[:30] in existing.content or existing.content[:30] in item.content:
                return True
        return False
        
    def query(self, query: str, limit: int = 10) -> List[MemoryItem]:
        results = []
        all_memories = self.episodic + self.long_term + list(self.working.values())
        for item in all_memories:
            if query.lower() in item.content.lower():
                results.append(item)
        return sorted(results, key=lambda x: x.importance, reverse=True)[:limit]
        
    def _log_to_spine(self, event_type: str, data: dict):
        record = {"type": event_type, "timestamp": time.time(), **data}
        with open(self.spine_path, "a") as f:
            f.write(json.dumps(record) + "\n")
            
    def _load(self):
        episodic_path = self.state_dir / "episodic.json"
        if episodic_path.exists():
            data = json.loads(episodic_path.read_text())
            for item in data:
                if isinstance(item.get('type'), str):
                    item['type'] = MemoryType(item['type'])
            self.episodic = [MemoryItem(**item) for item in data]
            
    def _save(self):
        def serialize(item):
            d = vars(item).copy()
            if isinstance(d.get('type'), MemoryType):
                d['type'] = d['type'].value
            return d
        (self.state_dir / "episodic.json").write_text(
            json.dumps([serialize(item) for item in self.episodic])
        )

if __name__ == "__main__":
    mem = MemorySystem()
    mem.record("Test memory item", MemoryType.EPISODIC, 0.9, ["test"])
    print(f"Recorded: {len(mem.episodic)} episodic memories")