#!/usr/bin/env python3
"""
Quantum-Inspired Routing
Routes tasks to optimal processing nodes based on complexity.
No actual quantum hardware needed - uses quantum-inspired algorithms.
"""
import math
import random
from typing import List, Dict, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

class TaskComplexity(Enum):
    TRIVIAL = 1      # Direct response
    SIMPLE = 2       # Basic transformation  
    MODERATE = 3     # Multi-step
    COMPLEX = 4      # Research + synthesis
    CRITICAL = 5     # Full autonomous

@dataclass
class Task:
    id: str
    description: str
    complexity: int      # 1-5
    modality: str        # text, code, math, reasoning, creation
    urgency: int        # 1-3
    context: List[str]   # Prior task IDs

@dataclass  
class RouteDecision:
    node: str
    estimated_time: float
    confidence: float
    alternatives: List[str]

class QuantumRouter:
    """
    Routes tasks using quantum-inspired decision making.
    Uses superposition principle: consider multiple paths simultaneously.
    Uses entanglement: link related tasks.
    Uses interference: amplify good paths, cancel bad ones.
    """
    
    def __init__(self):
        # Node capabilities
        self.nodes = {
            "fast": {"capacity": 10, "speed": 0.1, "types": ["text", "simple"]},
            "coder": {"capacity": 5, "speed": 0.5, "types": ["code", "math"]},
            "reason": {"capacity": 3, "speed": 1.0, "types": ["reasoning", "complex"]},
            "creative": {"capacity": 4, "speed": 0.8, "types": ["creation", "writing"]},
            "research": {"capacity": 2, "speed": 2.0, "types": ["research", "synthesis"]},
        }
        
        # Routing amplitude (quantum-inspired)
        self.amplitudes = {n: 1.0 for n in self.nodes}
        
    def _compute_amplitude(self, node: str, task: Task) -> float:
        """Compute routing amplitude - how suitable is this node?"""
        base = self.amplitudes.get(node, 0.1)
        
        # Type matching
        type_match = 1.0 if task.modality in self.nodes[node]["types"] else 0.3
        
        # Capacity availability
        capacity = self.nodes[node]["capacity"]
        load_factor = min(1.0, capacity / 3)  # Assume 2 tasks running
        
        # Complexity match
        complexity_match = {
            1: {"fast": 1.0, "coder": 0.5, "reason": 0.2, "creative": 0.8, "research": 0.1},
            2: {"fast": 0.8, "coder": 1.0, "reason": 0.4, "creative": 0.6, "research": 0.2},
            3: {"fast": 0.3, "coder": 0.8, "reason": 0.8, "creative": 0.7, "research": 0.5},
            4: {"fast": 0.1, "coder": 0.5, "reason": 1.0, "creative": 0.6, "research": 0.9},
            5: {"fast": 0.0, "coder": 0.3, "reason": 0.8, "creative": 0.5, "research": 1.0},
        }
        
        c_match = complexity_match.get(task.complexity, {}).get(node, 0.5)
        
        # Urgency boost
        urgency_boost = 1.0 + (task.urgency - 1) * 0.3
        
        return base * type_match * load_factor * c_match * urgency_boost
    
    def route(self, task: Task) -> RouteDecision:
        """Route task to optimal node using quantum-inspired selection"""
        # Compute amplitudes for all nodes
        amplitudes = {n: self._compute_amplitude(n, task) for n in self.nodes}
        
        # Normalize (like quantum state)
        total = sum(amplitudes.values())
        normalized = {n: a / total for n, a in amplitudes.items()}
        
        # Measure - collapse to most likely
        nodes = list(normalized.keys())
        probs = list(normalized.values())
        
        # Add randomness weighted by amplitude
        chosen = random.choice(nodes)
        
        # Confidence = probability
        confidence = normalized[chosen]
        
        # Alternatives
        sorted_nodes = sorted(normalized.items(), key=lambda x: -x[1])
        alternatives = [n for n, _ in sorted_nodes[1:3]]
        
        # Time estimate
        time_est = self.nodes[chosen]["speed"] * (1 + task.complexity * 0.5)
        
        return RouteDecision(
            node=chosen,
            estimated_time=time_est,
            confidence=confidence,
            alternatives=alternatives
        )
    
    def learn(self, task: Task, actual_time: float, success: bool):
        """Update amplitudes based on outcome"""
        node = self.route(task).node
        
        # If faster than expected, increase amplitude
        expected = self.nodes[node]["speed"] * (1 + task.complexity * 0.5)
        
        if success and actual_time < expected * 1.2:
            self.amplitudes[node] = min(2.0, self.amplitudes[node] * 1.1)
        elif not success:
            self.amplitudes[node] = max(0.2, self.amplitudes[node] * 0.8)

def demo_router():
    """Demo the quantum router"""
    router = QuantumRouter()
    
    print("=" * 50)
    print("QUANTUM-INSPIRED ROUTER")
    print("=" * 50)
    
    # Test tasks
    tasks = [
        Task("1", "What's the weather?", 1, "text", 1, []),
        Task("2", "Fix this bug", 3, "code", 2, []),
        Task("3", "Why is dark matter theoretical?", 4, "reasoning", 2, []),
        Task("4", "Write a poem about quantum", 2, "creation", 1, []),
        Task("5", "Research AGI safety", 5, "research", 3, []),
    ]
    
    for task in tasks:
        decision = router.route(task)
        print(f"\n📋 {task.description}")
        print(f"   → {decision.node} ({decision.confidence:.0%} confidence, {decision.estimated_time:.1f}s)")
        print(f"   Alternatives: {decision.alternatives}")
    
    return router

if __name__ == "__main__":
    demo_router()