#!/usr/bin/env python3
"""
EVEZ Swarm Orchestrator - Multi-agent coordination system
Coordinates multiple autonomous agents with task distribution
"""

import json
import time
import random
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class TaskPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"
    ERROR = "error"

@dataclass
class Task:
    id: str
    description: str
    priority: TaskPriority
    assigned_agent: Optional[str] = None
    status: str = "pending"
    created_at: str = ""
    completed_at: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None

@dataclass
class Agent:
    id: str
    name: str
    status: AgentStatus
    current_task: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    performance_score: float = 1.0
    tasks_completed: int = 0

class SwarmOrchestrator:
    """EVEZ-style multi-agent swarm coordinator"""
    
    def __init__(self, name: str = "Swarm-Orchestrator"):
        self.name = name
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []  # Task IDs
        self.event_log: List[Dict] = []
        
    def register_agent(self, agent_id: str, name: str, capabilities: List[str]) -> Agent:
        """Register a new agent in the swarm"""
        agent = Agent(
            id=agent_id,
            name=name,
            status=AgentStatus.IDLE,
            capabilities=capabilities
        )
        self.agents[agent_id] = agent
        self._log("AGENT_REGISTERED", {"agent_id": agent_id, "capabilities": capabilities})
        return agent
    
    def submit_task(self, description: str, priority: TaskPriority = TaskPriority.MEDIUM,
                   required_capabilities: Optional[List[str]] = None) -> Task:
        """Submit a new task to the swarm"""
        task = Task(
            id=str(uuid.uuid4())[:8],
            description=description,
            priority=priority,
            created_at=datetime.utcnow().isoformat() + "Z"
        )
        self.tasks[task.id] = task
        
        # Add to priority queue
        self.task_queue.append(task.id)
        self.task_queue.sort(key=lambda t: self.tasks[t].priority.value, reverse=True)
        
        self._log("TASK_SUBMITTED", {"task_id": task.id, "priority": priority.name})
        return task
    
    def assign_task(self, task_id: str) -> bool:
        """Assign a task to the best available agent"""
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        if task.assigned_agent:
            return False
            
        # Find best available agent
        best_agent = None
        best_score = -1
        
        for agent in self.agents.values():
            if agent.status != AgentStatus.IDLE:
                continue
                
            score = agent.performance_score
            if score > best_score:
                best_score = score
                best_agent = agent
                
        if not best_agent:
            return False
            
        # Assign task
        task.assigned_agent = best_agent.id
        task.status = "assigned"
        best_agent.status = AgentStatus.BUSY
        best_agent.current_task = task_id
        
        self._log("TASK_ASSIGNED", {
            "task_id": task_id,
            "agent_id": best_agent.id,
            "agent_name": best_agent.name
        })
        return True
    
    def complete_task(self, task_id: str, result: Dict) -> bool:
        """Mark task as completed"""
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        task.status = "completed"
        task.completed_at = datetime.utcnow().isoformat() + "Z"
        task.result = result
        
        # Update agent
        if task.assigned_agent and task.assigned_agent in self.agents:
            agent = self.agents[task.assigned_agent]
            agent.status = AgentStatus.IDLE
            agent.current_task = None
            agent.tasks_completed += 1
            # Update performance score
            agent.performance_score = min(2.0, agent.performance_score * 1.05)
        
        self._log("TASK_COMPLETED", {"task_id": task_id, "result": result})
        return True
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark task as failed"""
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        task.status = "failed"
        task.error = error
        
        # Update agent
        if task.assigned_agent and task.assigned_agent in self.agents:
            agent = self.agents[task.assigned_agent]
            agent.status = AgentStatus.IDLE
            agent.current_task = None
            agent.performance_score = max(0.5, agent.performance_score * 0.9)
        
        self._log("TASK_FAILED", {"task_id": task_id, "error": error})
        return True
    
    def run_cycle(self) -> Dict:
        """Run one orchestration cycle"""
        # Assign pending tasks
        assigned = 0
        for task_id in list(self.task_queue):
            task = self.tasks[task_id]
            if task.status == "pending" and not task.assigned_agent:
                if self.assign_task(task_id):
                    assigned += 1
        
        # Simulate task execution (in real system, this would be async)
        for agent in self.agents.values():
            if agent.status == AgentStatus.BUSY and agent.current_task:
                # Simulate completion
                if random.random() > 0.7:
                    self.complete_task(agent.current_task, {"status": "success"})
        
        return {
            "agents": len(self.agents),
            "tasks_pending": len([t for t in self.tasks.values() if t.status == "pending"]),
            "tasks_active": len([t for t in self.tasks.values() if t.status == "assigned"]),
            "tasks_completed": len([t for t in self.tasks.values() if t.status == "completed"]),
            "assigned_this_cycle": assigned
        }
    
    def _log(self, event_type: str, data: Dict):
        self.event_log.append({
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": data
        })
    
    def get_status(self) -> Dict:
        agent_states = {
            aid: {
                "name": a.name,
                "status": a.status.value,
                "tasks_completed": a.tasks_completed,
                "performance": a.performance_score
            }
            for aid, a in self.agents.items()
        }
        
        return {
            "name": self.name,
            "total_agents": len(self.agents),
            "total_tasks": len(self.tasks),
            "agent_states": agent_states,
            "events": len(self.event_log)
        }


# Demo
if __name__ == "__main__":
    swarm = SwarmOrchestrator("EVEZ-Swarm")
    
    # Register agents
    swarm.register_agent("agent-1", "Alpha", ["search", "analyze"])
    swarm.register_agent("agent-2", "Beta", ["code", "debug"])
    swarm.register_agent("agent-3", "Gamma", ["finance", "trade"])
    
    print("=== EVEZ Swarm Orchestrator ===\n")
    
    # Submit tasks
    swarm.submit_task("Analyze market trends", TaskPriority.HIGH, ["analyze"])
    swarm.submit_task("Write trading bot", TaskPriority.CRITICAL, ["code"])
    swarm.submit_task("Review portfolio", TaskPriority.MEDIUM, ["finance"])
    swarm.submit_task("Debug API endpoint", TaskPriority.HIGH, ["debug"])
    swarm.submit_task("Research competitors", TaskPriority.LOW, ["search"])
    
    print(f"Initial tasks: {len(swarm.tasks)}")
    
    # Run several cycles
    for i in range(10):
        result = swarm.run_cycle()
        if result["assigned_this_cycle"] > 0 or result["tasks_completed"] > 0:
            print(f"Cycle {i+1}: assigned={result['assigned_this_cycle']}, "
                  f"active={result['tasks_active']}, completed={result['tasks_completed']}")
    
    print("\n=== Swarm Status ===")
    print(json.dumps(swarm.get_status(), indent=2))