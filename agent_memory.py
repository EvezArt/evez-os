#!/usr/bin/env python3
"""
Agent Memory System - Fast context retrieval for agents
"""
import json
from pathlib import Path
from datetime import datetime

class AgentMemory:
    def __init__(self, workspace):
        self.workspace = Path(workspace)
        self.memory_file = self.workspace / "memory" / "agent_context.json"
        
    def store(self, key, value):
        data = self.load()
        data[key] = {"value": value, "ts": datetime.now().isoformat()}
        self.save(data)
        
    def retrieve(self, key):
        data = self.load()
        return data.get(key, {}).get("value")
    
    def recent(self, limit=10):
        data = self.load()
        items = list(data.items())[-limit:]
        return {k: v["value"] for k, v in items}
        
    def load(self):
        if self.memory_file.exists():
            return json.loads(self.memory_file.read_text())
        return {}
        
    def save(self, data):
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.memory_file.write_text(json.dumps(data, indent=2))

if __name__ == "__main__":
    m = AgentMemory("/root/.openclaw/workspace")
    print("AgentMemory ready")
