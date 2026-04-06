#!/usr/bin/env python3
"""
Task Spawner - Multi-Agent Parallel Execution
Spawns quantum agents that improve their own execution.
"""
import random
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import threading

@dataclass
class Agent:
    """A quantum agent that can spawn and improve"""
    id: str
    name: str
    state: str          # idle, running, improving, spawning
    capability: str     # text, code, reason, create, research
    efficiency: float  # 0-1, measures how well it learns
    spawn_count: int = 0
    tasks_completed: int = 0
    created_at: str = ""

@dataclass
class SpawnConfig:
    """Configuration for spawning new agents"""
    max_agents: int = 10
    spawn_threshold: float = 0.7  # efficiency needed to spawn
    improvement_rate: float = 0.1
    parallelism: int = 4

class TaskSpawner:
    """
    Spawns agents that improve their own execution.
    - Agents can spawn new agents
    - Self-improvement through feedback
    - Parallel task execution
    - Negative latency through concurrency
    """
    
    def __init__(self, config: SpawnConfig = None):
        self.config = config or SpawnConfig()
        self.agents: Dict[str, Agent] = {}
        self.task_queue: deque = deque(maxlen=100)
        self.results: Dict[str, Any] = {}
        self.spawn_lock = threading.Lock()
        self.next_id = 1
        self.history = deque(maxlen=50)
        
        # Spawn initial agents
        self._spawn_initial_agents()
    
    def _spawn_initial_agents(self):
        """Create initial agent pool"""
        capabilities = ["text", "code", "reason", "create", "research"]
        for cap in capabilities:
            agent = Agent(
                id=f"agent_{self.next_id}",
                name=f"{cap}_agent",
                state="idle",
                capability=cap,
                efficiency=0.5,
                created_at=datetime.utcnow().isoformat()
            )
            self.agents[agent.id] = agent
            self.next_id += 1
    
    def spawn_agent(self, capability: str, parent_id: str = None) -> Optional[Agent]:
        """Spawn a new agent if conditions allow"""
        if len(self.agents) >= self.config.max_agents:
            return None
        
        # Check efficiency threshold
        if parent_id:
            parent = self.agents.get(parent_id)
            if parent and parent.efficiency < self.config.spawn_threshold:
                return None
        
        # Create new agent
        agent = Agent(
            id=f"agent_{self.next_id}",
            name=f"{capability}_spawn_{self.next_id}",
            state="idle",
            capability=capability,
            efficiency=0.5 if parent_id else 0.3,
            spawn_count=0,
            created_at=datetime.utcnow().isoformat()
        )
        
        if parent_id:
            parent = self.agents.get(parent_id)
            if parent:
                parent.spawn_count += 1
        
        self.agents[agent.id] = agent
        self.next_id += 1
        
        return agent
    
    def assign_task(self, task: Dict) -> Optional[str]:
        """Assign task to best available agent"""
        capability = task.get("capability", "text")
        
        # Find idle agent with matching capability
        for agent in self.agents.values():
            if agent.state == "idle" and agent.capability == capability:
                agent.state = "running"
                agent.tasks_completed += 1
                self.task_queue.append({
                    "task": task,
                    "agent_id": agent.id,
                    "started_at": datetime.utcnow().isoformat()
                })
                return agent.id
        
        # Find any idle agent
        for agent in self.agents.values():
            if agent.state == "idle":
                agent.state = "running"
                agent.tasks_completed += 1
                return agent.id
        
        return None  # No available agents
    
    def complete_task(self, agent_id: str, success: bool, improvement: float = 0):
        """Complete task and update agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            return
        
        agent.state = "idle"
        
        # Update efficiency
        if success:
            agent.efficiency = min(1.0, agent.efficiency + self.config.improvement_rate)
        else:
            agent.efficiency = max(0.1, agent.efficiency - self.config.improvement_rate * 0.5)
        
        self.history.append({
            "agent_id": agent_id,
            "success": success,
            "efficiency": agent.efficiency,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Check if agent can spawn
        if agent.efficiency > self.config.spawn_threshold and agent.spawn_count < 3:
            new_cap = random.choice(["text", "code", "reason", "create", "research"])
            spawned = self.spawn_agent(new_cap, agent_id)
            if spawned:
                agent.state = "spawning"
    
    def get_stats(self) -> Dict:
        """Get spawner statistics"""
        total_eff = sum(a.efficiency for a in self.agents.values()) / len(self.agents)
        
        return {
            "total_agents": len(self.agents),
            "max_agents": self.config.max_agents,
            "average_efficiency": total_eff,
            "tasks_completed": sum(a.tasks_completed for a in self.agents.values()),
            "total_spawns": sum(a.spawn_count for a in self.agents.values()),
            "parallelism": self.config.parallelism,
            "negative_latency_factor": self._calc_latency_factor()
        }
    
    def _calc_latency_factor(self) -> float:
        """Calculate negative latency from parallelism"""
        idle_agents = sum(1 for a in self.agents.values() if a.state == "idle")
        return idle_agents / len(self.agents) if self.agents else 0
    
    def optimize_spawns(self) -> Dict:
        """Optimize agent spawning for maximum throughput"""
        stats = self.get_stats()
        
        if stats["average_efficiency"] > 0.6 and stats["total_agents"] < stats["max_agents"]:
            # High efficiency - spawn more
            return {"action": "spawn", "count": min(3, stats["max_agents"] - stats["total_agents"])}
        elif stats["negative_latency_factor"] < 0.3:
            # Low parallelism - improve efficiency
            return {"action": "improve", "target": "low_efficiency_agents"}
        else:
            return {"action": "maintain", "changes": 0}

def demo_spawner():
    """Demo the task spawner"""
    spawner = TaskSpawner()
    
    print("=" * 50)
    print("QUANTUM AGENT SPAWNER")
    print("=" * 50)
    
    # Assign tasks
    tasks = [
        {"id": "t1", "type": "research", "capability": "research"},
        {"id": "t2", "type": "create", "capability": "create"},
        {"id": "t3", "type": "code", "capability": "code"},
        {"id": "t4", "type": "reason", "capability": "reason"},
        {"id": "t5", "type": "text", "capability": "text"},
    ]
    
    print("\n📋 Task Assignment:")
    for task in tasks:
        agent_id = spawner.assign_task(task)
        print(f"   {task['id']} → {agent_id}")
    
    # Complete tasks (simulated)
    print("\n✅ Task Completion:")
    for agent_id in list(spawner.agents.keys())[:3]:
        spawner.complete_task(agent_id, True, 0.1)
        print(f"   {agent_id} completed")
    
    # Spawn decision
    print("\n🧬 Spawn Decision:")
    optimization = spawner.optimize_spawns()
    print(f"   {optimization['action']}")
    
    # Stats
    print("\n📊 Stats:")
    stats = spawner.get_stats()
    print(f"   Agents: {stats['total_agents']}/{stats['max_agents']}")
    print(f"   Efficiency: {stats['average_efficiency']:.0%}")
    print(f"   Parallelism: {stats['parallelism']}x")
    print(f"   Negative latency factor: {stats['negative_latency_factor']:.0%}")
    
    return spawner

if __name__ == "__main__":
    demo_spawner()