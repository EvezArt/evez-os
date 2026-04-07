#!/usr/bin/env python3
"""
Autonomous Decision Agent - EVEZ-style RL agent with hot-swapping
Uses contextual bandit approach for backend allocation (stdlib only)
"""

import json
import random
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import uuid

class BackendType(Enum):
    LOCAL = "local"
    QUANTUM = "quantum"
    HYBRID = "hybrid"
    REMOTE = "remote"

@dataclass
class Decision:
    backend: BackendType
    estimated_latency: float
    qubits_required: int
    route_to_t3: bool

class ContextualBanditAgent:
    """EVEZ-style autonomous agent with hot-swapping capability"""
    
    def __init__(self, name: str = "EVEZ-Agent"):
        self.name = name
        self.learning_rate = 0.1
        self.gamma = 0.99
        self.epsilon = 0.1
        
        # Q-table with simple state discretization
        # State: complexity (10 bins) * confidence (5 bins) = 50 states
        # Actions: 4 backends
        self.Q = [[0.0 for _ in range(4)] for _ in range(50)]
        self.counts = [[0 for _ in range(4)] for _ in range(50)]
        
        # Dynamic thresholds (hot-swappable)
        self.thresholds = {
            BackendType.LOCAL: 22.0,
            BackendType.QUANTUM: 28.6,
            BackendType.HYBRID: 30.0,
            BackendType.REMOTE: float('inf')
        }
        
        # History for learning
        self.history: List[Dict] = []
        
    def _discretize(self, complexity: float, confidence: float) -> int:
        """Map complexity + confidence to state index"""
        c_bin = min(9, int((complexity - 10) / 4))  # 0-9
        f_bin = min(4, int(confidence / 0.3))  # 0-4
        return c_bin * 5 + f_bin
    
    def _get_action(self, state: int) -> int:
        """Epsilon-greedy action selection"""
        if random.random() < self.epsilon:
            return random.randint(0, 3)
        # Argmax Q
        return max(range(4), key=lambda a: self.Q[state][a])
    
    def _get_backend(self, action: int) -> BackendType:
        return [BackendType.LOCAL, BackendType.QUANTUM, 
                BackendType.HYBRID, BackendType.REMOTE][action]
    
    def decide(self, complexity: float, confidence: float) -> Decision:
        """Make allocation decision"""
        state = self._discretize(complexity, confidence)
        action = self._get_action(state)
        backend = self._get_backend(action)
        
        # Estimate metrics
        latency = self._estimate_latency(backend, complexity)
        qubits = self._estimate_qubits(backend, complexity)
        route_t3 = backend != BackendType.LOCAL
        
        decision = Decision(
            backend=backend,
            estimated_latency=latency,
            qubits_required=qubits,
            route_to_t3=route_t3
        )
        
        self.history.append({
            "state": state,
            "action": action,
            "decision": decision,
            "complexity": complexity,
            "confidence": confidence
        })
        
        return decision
    
    def _estimate_latency(self, backend: BackendType, complexity: float) -> float:
        base = {BackendType.LOCAL: 3.15, BackendType.QUANTUM: 6.45,
                BackendType.HYBRID: 28.25, BackendType.REMOTE: 123.25}
        return base.get(backend, 50.0) * (1 + (complexity - 20) / 50)
    
    def _estimate_qubits(self, backend: BackendType, complexity: float) -> int:
        if backend == BackendType.QUANTUM:
            return int(18 + complexity * 0.8)
        elif backend == BackendType.REMOTE:
            return int(complexity * 1.5)
        return 0
    
    def learn(self, actual_latency: float, success: bool):
        """Update Q-table from outcome"""
        if not self.history:
            return
            
        entry = self.history[-1]
        state = entry["state"]
        action = entry["action"]
        
        # Reward: negative latency + success bonus
        reward = -actual_latency / 1000 + (10 if success else -5)
        
        # Q-learning update
        old_q = self.Q[state][action]
        max_q = max(self.Q[state])
        self.Q[state][action] += self.learning_rate * (reward + self.gamma * max_q - old_q)
        self.counts[state][action] += 1
    
    def hot_swap_thresholds(self, new_thresholds: Dict[BackendType, float]):
        """Update thresholds without restart"""
        self.thresholds.update(new_thresholds)
        print(f"[{self.name}] Hot-swapped thresholds: {new_thresholds}")
    
    def get_stats(self) -> Dict:
        counts = {}
        for i, bt in enumerate([BackendType.LOCAL, BackendType.QUANTUM, BackendType.HYBRID, BackendType.REMOTE]):
            counts[bt.value] = sum(row[i] for row in self.counts)
        
        return {
            "total_decisions": len(self.history),
            "action_counts": counts,
            "thresholds": {k.value: v for k, v in self.thresholds.items()},
            "avg_q": sum(sum(row) for row in self.Q) / len(self.Q)
        }


# Demo
if __name__ == "__main__":
    agent = ContextualBanditAgent("EVEZ-001")
    
    print("=== EVEZ Autonomous Agent ===")
    
    for i in range(20):
        complexity = random.uniform(15, 45)
        confidence = random.uniform(0.3, 1.2)
        decision = agent.decide(complexity, confidence)
        
        actual_latency = decision.estimated_latency * random.uniform(0.8, 1.2)
        success = random.random() > 0.2
        
        agent.learn(actual_latency, success)
        
        print(f"[{i+1:2d}] C:{complexity:5.1f} Conf:{confidence:.2f} → {decision.backend.value:8s}")
    
    print("\n=== Agent Stats ===")
    print(json.dumps(agent.get_stats(), indent=2))