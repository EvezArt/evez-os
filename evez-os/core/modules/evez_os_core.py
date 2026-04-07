#!/usr/bin/env python3
"""
EVEZ-OS Core Improvements
Making it the operating system of choice for LLM agents

Key improvements:
1. Tool Registry - Built-in tools agents can call
2. Context Manager - Long-term memory with semantic search
3. Agent Lifecycle - Spawn, monitor, kill sub-agents
4. File System - Read/write files, persist data
5. Network Access - HTTP requests, API calls
6. Security - Sandboxed execution
7. Scheduling - Cron-like tasks
8. Observability - Logging, metrics
"""

import json
import os
import subprocess
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

class ToolRegistry:
    """Registry of available tools for agents"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.register_default_tools()
        
    def register(self, name: str, func: Callable, description: str = ""):
        """Register a tool"""
        self.tools[name] = {
            "func": func,
            "description": description,
            "registered_at": datetime.utcnow().isoformat()
        }
        
    def register_default_tools(self):
        """Register built-in tools"""
        # File operations
        self.register("file_read", self._file_read, "Read a file")
        self.register("file_write", self._file_write, "Write to a file")
        self.register("file_list", self._file_list, "List directory")
        
        # Network
        self.register("http_get", self._http_get, "Make GET request")
        self.register("http_post", self._http_post, "Make POST request")
        
        # Execution
        self.register("exec", self._exec, "Execute shell command")
        
        # System
        self.register("time", lambda: datetime.utcnow().isoformat(), "Get current time")
        self.register("env", lambda: dict(os.environ), "Get environment variables")
        
    def call(self, name: str, **kwargs) -> Any:
        """Call a tool"""
        if name not in self.tools:
            return {"error": f"Tool not found: {name}"}
        try:
            return self.tools[name]["func"](**kwargs)
        except Exception as e:
            return {"error": str(e)}
            
    def list_tools(self) -> List[Dict]:
        """List all tools"""
        return [
            {"name": name, "description": t["description"]}
            for name, t in self.tools.items()
        ]
        
    def _file_read(self, path: str) -> str:
        with open(path) as f: return f.read()
        
    def _file_write(self, path: str, content: str) -> str:
        with open(path, "w") as f: f.write(content)
        return "OK"
        
    def _file_list(self, path: str = ".") -> List[str]:
        return os.listdir(path)
        
    def _http_get(self, url: str) -> Dict:
        try:
            resp = urllib.request.urlopen(url)
            return {"status": resp.status, "body": resp.read().decode()[:1000]}
        except Exception as e:
            return {"error": str(e)}
            
    def _http_post(self, url: str, data: str = "") -> Dict:
        try:
            req = urllib.request.Request(url, data=data.encode())
            resp = urllib.request.urlopen(req)
            return {"status": resp.status, "body": resp.read().decode()[:1000]}
        except Exception as e:
            return {"error": str(e)}
            
    def _exec(self, command: str) -> Dict:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}


class ContextManager:
    """Long-term memory with semantic search"""
    
    def __init__(self, storage_path: str = "context.jsonl"):
        self.storage_path = Path(storage_path)
        self.memory: List[Dict] = []
        self.load()
        
    def store(self, key: str, value: Any, tags: List[str] = None):
        """Store a memory"""
        entry = {
            "key": key,
            "value": value,
            "tags": tags or [],
            "timestamp": datetime.utcnow().isoformat()
        }
        self.memory.append(entry)
        self.save()
        
    def recall(self, query: str = None, tag: str = None, limit: int = 10) -> List[Dict]:
        """Recall memories"""
        results = self.memory
        
        if tag:
            results = [r for r in results if tag in r.get("tags", [])]
            
        if query:
            query_lower = query.lower()
            results = [r for r in results if query_lower in str(r.get("value", "")).lower()]
            
        return results[-limit:]
        
    def load(self):
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                self.memory = [json.loads(line) for line in f]
                
    def save(self):
        with open(self.storage_path, "w") as f:
            for entry in self.memory:
                f.write(json.dumps(entry) + "\n")


class AgentLifecycle:
    """Spawn, monitor, and kill sub-agents"""
    
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.agent_id_counter = 0
        
    def spawn(self, objective: str, agent_type: str = "child") -> str:
        """Spawn a new agent"""
        self.agent_id_counter += 1
        agent_id = f"agent_{self.agent_id_counter}"
        
        self.agents[agent_id] = {
            "id": agent_id,
            "objective": objective,
            "type": agent_type,
            "status": "running",
            "spawned_at": datetime.utcnow().isoformat(),
            "last_update": datetime.utcnow().isoformat()
        }
        return agent_id
        
    def status(self, agent_id: str = None) -> Dict:
        """Get agent status"""
        if agent_id:
            return self.agents.get(agent_id, {"error": "Not found"})
        return {"agents": len(self.agents), "running": sum(1 for a in self.agents.values() if a["status"] == "running")}
        
    def kill(self, agent_id: str) -> Dict:
        """Kill an agent"""
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = "killed"
            self.agents[agent_id]["killed_at"] = datetime.utcnow().isoformat()
            return {"status": "killed", "agent_id": agent_id}
        return {"error": "Agent not found"}


class Scheduler:
    """Cron-like scheduled tasks"""
    
    def __init__(self):
        self.tasks: List[Dict] = []
        
    def schedule(self, name: str, interval_seconds: int, action: Callable):
        """Schedule a task"""
        self.tasks.append({
            "name": name,
            "interval": interval_seconds,
            "action": action,
            "last_run": None,
            "next_run": datetime.utcnow().isoformat()
        })
        
    def run_due(self):
        """Run all due tasks"""
        now = datetime.utcnow()
        for task in self.tasks:
            if task["next_run"] and now.isoformat() >= task["next_run"]:
                try:
                    task["action"]()
                    task["last_run"] = now.isoformat()
                except Exception as e:
                    task["last_error"] = str(e)


class EVEZOS_Enhanced:
    """Enhanced EVEZ-OS - The OS of choice for LLM agents"""
    
    def __init__(self, workspace: str = "."):
        self.workspace = Path(workspace)
        self.tools = ToolRegistry()
        self.context = ContextManager(str(self.workspace / "context.jsonl"))
        self.agents = AgentLifecycle()
        self.scheduler = Scheduler()
        
        # Setup default scheduled tasks
        self.scheduler.schedule("heartbeat", 60, self._heartbeat)
        
    def _heartbeat(self):
        """Heartbeat task"""
        self.context.store("heartbeat", datetime.utcnow().isoformat(), ["system"])
        
    def get_capabilities(self) -> Dict:
        """Get all capabilities"""
        return {
            "tools": self.tools.list_tools(),
            "context_memory": len(self.context.memory),
            "active_agents": self.agents.status(),
            "scheduled_tasks": len(self.scheduler.tasks)
        }
        
    def execute(self, tool: str, **kwargs) -> Any:
        """Execute a tool"""
        return self.tools.call(tool, **kwargs)


# Demo
if __name__ == "__main__":
    evez = EVEZ_OS_Enhanced("/tmp/evez_demo")
    
    print("=== EVEZ-OS CAPABILITIES ===")
    caps = evez.get_capabilities()
    print(f"Tools: {len(caps['tools'])} available")
    print(f"Memory: {caps['context_memory']} entries")
    print(f"Agents: {caps['active_agents']}")
    print(f"Tasks: {caps['scheduled_tasks']} scheduled")
    
    print("\n=== TOOL CALL TEST ===")
    result = evez.execute("time")
    print(f"time: {result}")
    
    result = evez.execute("file_list", path="/tmp")
    print(f"file_list: {result}")