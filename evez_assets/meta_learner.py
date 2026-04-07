#!/usr/bin/env python3
"""
EVEZ Meta-Learner - Learning to learn
Analyzes own performance and generates improved strategies
"""

import json
import random
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

@dataclass
class Strategy:
    id: str
    name: str
    parameters: Dict
    performance_history: List[float] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    
@dataclass
class LearningEntry:
    timestamp: str
    context: Dict
    action: str
    outcome: float
    metadata: Dict = field(default_factory=dict)

class MetaLearner:
    """EVEZ Meta-Learner - learns to improve learning"""
    
    def __init__(self, name: str = "Meta-Learner"):
        self.name = name
        self.strategies: Dict[str, Strategy] = {}
        self.learning_history: List[LearningRecord] = []
        self.current_strategy: Optional[str] = None
        
        # Default strategies
        self._init_strategies()
        
    def _init_strategies(self):
        """Initialize base strategies"""
        self.strategies["explore-random"] = Strategy(
            id="explore-random",
            name="Random Exploration",
            parameters={"exploration_rate": 0.3, "sample_size": 5}
        )
        self.strategies["exploit-best"] = Strategy(
            id="exploit-best", 
            name="Exploit Best Performing",
            parameters={"lookback": 10, "threshold": 0.7}
        )
        self.strategies["adaptive"] = Strategy(
            id="adaptive",
            name="Adaptive Strategy Switching",
            parameters={"switch_threshold": 0.2, "evaluation_period": 5}
        )
        self.strategies["meta-explore"] = Strategy(
            id="meta-explore",
            name="Meta-Learning Exploration",
            parameters={"hypothesis_count": 3, "test_cycles": 2}
        )
        
        self.current_strategy = "adaptive"
    
    def record(self, context: Dict, action: str, outcome: float, metadata: Optional[Dict] = None):
        """Record a learning event"""
        record = LearningEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            context=context,
            action=action,
            outcome=outcome,
            metadata=metadata or {}
        )
        self.learning_history.append(record)
        
        # Update current strategy performance
        if self.current_strategy:
            strategy = self.strategies[self.current_strategy]
            strategy.performance_history.append(outcome)
            if outcome > 0:
                strategy.success_count += 1
            else:
                strategy.failure_count += 1
    
    def evaluate_strategies(self) -> Dict[str, float]:
        """Evaluate all strategies"""
        scores = {}
        for sid, strategy in self.strategies.items():
            if not strategy.performance_history:
                scores[sid] = 0.5
                continue
                
            recent = strategy.performance_history[-10:]
            avg = sum(recent) / len(recent)
            
            # Win rate bonus
            total = strategy.success_count + strategy.failure_count
            win_rate = strategy.success_count / max(1, total)
            
            # Combined score
            scores[sid] = (avg * 0.7) + (win_rate * 0.3)
            
        return scores
    
    def select_strategy(self) -> str:
        """Select best strategy based on evaluation"""
        scores = self.evaluate_strategies()
        
        # Add some exploration (epsilon-greedy)
        if random.random() < 0.2:
            return random.choice(list(self.strategies.keys()))
        
        # Return best
        best = max(scores.items(), key=lambda x: x[1])
        self.current_strategy = best[0]
        return best[0]
    
    def generate_hypothesis(self) -> Dict:
        """Generate a hypothesis about improving performance"""
        # Analyze recent history
        recent = self.learning_history[-20:] if len(self.learning_history) >= 20 else self.learning_history
        
        if not recent:
            return {"hypothesis": "No data yet", "confidence": 0.0}
        
        # Find patterns
        contexts = [r.context for r in recent]
        actions = [r.action for r in recent]
        outcomes = [r.outcome for r in recent]
        
        # Simple pattern: best actions by context
        action_scores = defaultdict(list)
        for r in recent:
            action_scores[r.action].append(r.outcome)
        
        best_action = max(action_scores.items(), key=lambda x: sum(x[1])/len(x[1]))
        
        hypothesis = {
            "hypothesis": f"Action '{best_action[0]}' performs best",
            "confidence": len(recent) / 20,
            "evidence": f"avg outcome: {sum(best_action[1])/len(best_action[1]):.3f}",
            "sample_size": len(recent)
        }
        
        return hypothesis
    
    def create_new_strategy(self, name: str, parameters: Dict) -> Strategy:
        """Create a new strategy based on learned patterns"""
        strategy = Strategy(
            id=f"strategy-{len(self.strategies)}",
            name=name,
            parameters=parameters
        )
        self.strategies[strategy.id] = strategy
        return strategy
    
    def meta_learn(self) -> Dict:
        """Perform meta-learning - learn to learn better"""
        # Generate hypothesis
        hypothesis = self.generate_hypothesis()
        
        # Evaluate current strategy
        scores = self.evaluate_strategies()
        
        # Decide whether to switch
        current_score = scores.get(self.current_strategy, 0.5)
        best_score = max(scores.values())
        
        switch_needed = best_score - current_score > 0.2
        
        if switch_needed:
            new_strategy = self.select_strategy()
            self.current_strategy = new_strategy
        
        return {
            "current_strategy": self.current_strategy,
            "strategy_scores": scores,
            "switched": switch_needed,
            "hypothesis": hypothesis,
            "total_learning_events": len(self.learning_history),
            "total_strategies": len(self.strategies)
        }
    
    def get_insights(self) -> Dict:
        """Get insights from learning history"""
        if not self.learning_history:
            return {"insights": "No data yet"}
        
        # Action performance
        action_scores = defaultdict(lambda: {"success": 0, "total": 0})
        for record in self.learning_history:
            action_scores[record.action]["total"] += 1
            if record.outcome > 0:
                action_scores[record.action]["success"] += 1
        
        # Calculate win rates
        action_win_rates = {
            action: data["success"] / max(1, data["total"])
            for action, data in action_scores.items()
        }
        
        # Context patterns
        context_patterns = defaultdict(list)
        for record in self.learning_history:
            for key, value in record.context.items():
                context_patterns[f"{key}={value}"].append(record.outcome)
        
        context_avg = {
            ctx: sum(outcomes) / len(outcomes)
            for ctx, outcomes in context_patterns.items()
            if len(outcomes) >= 3
        }
        
        return {
            "action_performance": action_win_rates,
            "context_patterns": context_avg,
            "best_action": max(action_win_rates.items(), key=lambda x: x[1]) if action_win_rates else None,
            "total_events": len(self.learning_history)
        }


# Demo
if __name__ == "__main__":
    learner = MetaLearner("EVEZ-Meta")
    
    print("=== EVEZ Meta-Learner ===\n")
    
    # Simulate learning
    contexts = [{"domain": "finance"}, {"domain": "cognition"}, {"domain": "swarm"}, {"domain": "network"}]
    actions = ["optimize", "expand", "maintain", "restructure", "analyze"]
    
    for i in range(30):
        ctx = random.choice(contexts)
        act = random.choice(actions)
        outcome = random.uniform(-1, 1)
        
        # Add some skill correlation
        if act == "optimize" and ctx["domain"] == "finance":
            outcome += 0.3
            
        learner.record(ctx, act, outcome)
    
    # Meta-learn
    result = learner.meta_learn()
    print(f"Meta-Learning Result:")
    print(f"  Strategy: {result['current_strategy']}")
    print(f"  Switched: {result['switched']}")
    print(f"  Hypothesis: {result['hypothesis']['hypothesis']}")
    print(f"  Confidence: {result['hypothesis']['confidence']:.2f}")
    
    # Get insights
    insights = learner.get_insights()
    print(f"\nInsights:")
    print(f"  Best action: {insights['best_action']}")
    print(f"  Action performance: {insights['action_performance']}")