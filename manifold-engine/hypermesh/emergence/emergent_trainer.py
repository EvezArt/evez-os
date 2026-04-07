#!/usr/bin/env python3
"""
Emergent Training System
Self-improves by learning from its own outputs.
"""
import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque

@dataclass
class Experience:
    input: str
    output: str
    outcome: str
    improvement: float
    timestamp: str = ""

class EmergentTrainer:
    """
    Emergent trainer that self-improves.
    """
    
    def __init__(self):
        self.experiences = deque(maxlen=1000)
        self.patterns: Dict[str, float] = {}
        self.modifications = 0
        self.confidence_threshold = 0.7
        
    def observe(self, input_text: str, output_text: str, outcome: str):
        """Record an experience"""
        exp = Experience(
            input=input_text[:100],
            output=output_text[:100],
            outcome=outcome,
            improvement=1.0 if outcome == "success" else (-0.5 if outcome == "failure" else 0.0),
            timestamp=datetime.utcnow().isoformat()
        )
        self.experiences.append(exp)
        self._update_patterns(input_text, outcome)
    
    def _update_patterns(self, input_text: str, outcome: str):
        """Extract patterns from experience"""
        words = input_text.lower().split()
        
        for word in words:
            if len(word) > 3:
                if word not in self.patterns:
                    self.patterns[word] = 0.0
                
                delta = 0.1 if outcome == "success" else (-0.1 if outcome == "failure" else 0.0)
                # Tanh approximation
                self.patterns[word] = (math.tanh(self.patterns[word] + delta) if abs(self.patterns[word] + delta) < 10 else 
                                (1 if self.patterns[word] + delta > 0 else -1))
    
    def _get_success_patterns(self) -> List[Tuple[str, float]]:
        items = [(k, v) for k, v in self.patterns.items() if v > 0.3]
        return sorted(items, key=lambda x: -x[1])[:10]
    
    def _get_failure_patterns(self) -> List[Tuple[str, float]]:
        items = [(k, v) for k, v in self.patterns.items() if v < -0.2]
        return sorted(items, key=lambda x: x[1])[:10]
    
    def analyze(self) -> Dict:
        if not self.experiences:
            return {"status": "no data"}
        
        outcomes = {"success": 0, "failure": 0, "partial": 0}
        for e in self.experiences:
            outcomes[e.outcome] = outcomes.get(e.outcome, 0) + 1
        
        total = len(self.experiences)
        success_rate = outcomes["success"] / total
        
        return {
            "total_experiences": total,
            "success_rate": success_rate,
            "outcomes": outcomes,
            "patterns_learned": len(self.patterns),
            "modifications": self.modifications,
            "top_patterns": self._get_success_patterns()[:5],
            "bottom_patterns": self._get_failure_patterns()[:5]
        }
    
    def adapt(self) -> Dict:
        analysis = self.analyze()
        
        if analysis.get("success_rate", 0) > self.confidence_threshold:
            return {"action": "maintain", "changes": 0}
        
        failures = self._get_failure_patterns()
        
        if failures:
            return {
                "action": "avoid_patterns",
                "patterns": [f[0] for f in failures[:3]],
                "changes": len(failures)
            }
        
        return {"action": "explore", "changes": 0}
    
    def route_decision(self, input_text: str) -> Dict:
        words = input_text.lower().split()
        
        score = 0.0
        matched = []
        
        for word in words:
            if len(word) > 3 and word in self.patterns:
                score += self.patterns[word]
                matched.append((word, self.patterns[word]))
        
        if score > 0.5:
            confidence = "high"
            strategy = "exploit"
        elif score < -0.3:
            confidence = "low"
            strategy = "explore"
        else:
            confidence = "medium"
            strategy = "balance"
        
        return {
            "strategy": strategy,
            "confidence": confidence,
            "pattern_score": score,
            "matched": matched[:5]
        }
    
    def generate_synthetic_task(self) -> str:
        analysis = self.analyze()
        topics = ["quantum", "neural", "emergence", "complexity", "information"]
        
        for topic in topics:
            if topic not in self.patterns or abs(self.patterns.get(topic, 0)) < 0.2:
                return f"Explain {topic} in simple terms"
        
        return "What is the relationship between entropy and information?"

def demo_trainer():
    trainer = EmergentTrainer()
    
    print("=" * 50)
    print("EMERGENT TRAINING SYSTEM")
    print("=" * 50)
    
    experiences = [
        ("Explain quantum entanglement", "Particles become correlated", "success"),
        ("Solve 2+2", "4", "success"),
        ("Why is sky blue", "Rayleigh scattering", "success"),
        ("What is the meaning of life", "42", "partial"),
        ("Explain the undefined", "", "failure"),
    ]
    
    for input_text, output, outcome in experiences:
        trainer.observe(input_text, output, outcome)
    
    print("\n📊 Analysis:")
    analysis = trainer.analyze()
    print(f"   Total: {analysis['total_experiences']}")
    print(f"   Success rate: {analysis['success_rate']:.0%}")
    print(f"   Patterns: {analysis['patterns_learned']}")
    
    print("\n🎯 Route Decision for 'Explain quantum':")
    decision = trainer.route_decision("Explain quantum mechanics")
    print(f"   Strategy: {decision['strategy']}")
    print(f"   Confidence: {decision['confidence']}")
    
    print("\n🔧 Self-Adapt:")
    adaptation = trainer.adapt()
    print(f"   Action: {adaptation['action']}")
    
    print("\n🆕 Synthetic Task:")
    new_task = trainer.generate_synthetic_task()
    print(f"   {new_task}")
    
    return trainer

if __name__ == "__main__":
    demo_trainer()