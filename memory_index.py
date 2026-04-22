#!/usr/bin/env python3
"""
Memory Index - Fast semantic search of memories
"""
import json
from pathlib import Path

class MemoryIndex:
    def __init__(self, memory_dir="/root/.openclaw/workspace/memory"):
        self.memory_dir = Path(memory_dir)
        self.index = {}
        
    def build_index(self):
        """Build search index"""
        for f in self.memory_dir.glob("*.md"):
            content = f.read_text()
            self.index[f.name] = {"words": set(content.split()), "size": len(content)}
        return {"indexed": len(self.index)}
    
    def search(self, query):
        """Search memories"""
        query_words = set(query.lower().split())
        results = []
        for name, data in self.index.items():
            overlap = len(query_words & data["words"])
            if overlap > 0:
                results.append({"file": name, "match": overlap})
        return sorted(results, key=lambda x: -x["match"])[:5]

if __name__ == "__main__":
    m = MemoryIndex()
    print(m.build_index())
