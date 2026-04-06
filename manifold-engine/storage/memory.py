#!/usr/bin/env python3
"""
Persistent Memory System - Local-first AI memory
Stores and retrieves memories with semantic search.
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

MEMORY_DIR = Path(__file__).parent / "memory"
MEMORY_DIR.mkdir(exist_ok=True)

class MemoryStore:
    def __init__(self):
        self.memories = []
        self.load()
    
    def load(self):
        """Load memories from disk"""
        f = MEMORY_DIR / "memories.json"
        if f.exists():
            self.memories = json.loads(f.read_text())
        else:
            self.memories = []
    
    def save(self):
        """Persist to disk"""
        (MEMORY_DIR / "memories.json").write_text(json.dumps(self.memories, indent=2))
    
    def add(self, content: str, metadata: Dict = None):
        """Store a new memory"""
        memory = {
            "id": len(self.memories) + 1,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "access_count": 0
        }
        self.memories.append(memory)
        self.save()
        return memory["id"]
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Simple keyword search (replace with embeddings for semantic)"""
        query_lower = query.lower()
        results = []
        
        for m in self.memories:
            score = 0
            # Title/keyword match
            if query_lower in m["content"].lower():
                score += 1
            # Tag matches
            for tag in m.get("metadata", {}).get("tags", []):
                if tag.lower() in query_lower:
                    score += 2
            
            if score > 0:
                m["_score"] = score
                results.append(m)
        
        results.sort(key=lambda x: x.get("_score", 0), reverse=True)
        
        # Update access count
        for r in results[:limit]:
            for m in self.memories:
                if m["id"] == r["id"]:
                    m["access_count"] = m.get("access_count", 0) + 1
        self.save()
        
        return results[:limit]
    
    def get(self, memory_id: int) -> Optional[Dict]:
        """Retrieve by ID"""
        for m in self.memories:
            if m["id"] == memory_id:
                return m
        return None
    
    def list_all(self, limit: int = 20) -> List[Dict]:
        """List recent memories"""
        return sorted(self.memories, key=lambda x: x["timestamp"], reverse=True)[:limit]

def demo_memory():
    """Demo the memory system"""
    store = MemoryStore()
    
    print("=" * 40)
    print("PERSISTENT MEMORY DEMO")
    print("=" * 40)
    
    # Add memories
    print("\n1. Adding memories...")
    store.add("User prefers short responses", {"tags": ["preference", "style"]})
    store.add("Gateway runs on port 3001", {"tags": ["config", "technical"]})
    store.add("Browser automation skill available", {"tags": ["skill", "automation"]})
    store.add("Profit engine ledger at /profit-engine/", {"tags": ["finance", "tracking"]})
    
    print(f"   Stored {len(store.memories)} memories")
    
    # Search
    print("\n2. Searching 'preference'...")
    results = store.search("preference")
    for r in results:
        print(f"   - [{r['id']}] {r['content'][:50]}...")
    
    # List all
    print("\n3. All memories:")
    for m in store.list_all():
        print(f"   - [{m['id']}] {m['content'][:40]}")
    
    return store

if __name__ == "__main__":
    demo_memory()