#!/usr/bin/env python3
"""
EVEZ Pattern Detector - Cross-domain correlation engine
Finds hidden patterns across all system components
"""

import json
import random
import math
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

@dataclass
class Pattern:
    id: str
    domain_a: str
    domain_b: str
    correlation: float
    strength: str  # weak, moderate, strong
    evidence: List[str]
    discovered_at: str

class PatternDetector:
    """EVEZ-style cross-domain pattern detection"""
    
    def __init__(self):
        self.patterns: List[Pattern] = []
        self.domains = [
            "spine", "agent", "memory", "cognition", 
            "loop", "swarm", "finance", "network"
        ]
        self.correlation_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)
        
    def measure_correlation(self, domain_a: str, domain_b: str) -> float:
        """Calculate correlation between two domains"""
        # Simulated correlation (in real system, analyze actual data)
        if domain_a == domain_b:
            return 1.0
            
        # Deterministic but varied based on domain pair
        hash_val = hash(f"{domain_a}:{domain_b}") % 1000
        base = (hash_val / 1000) * 2 - 1  # -1 to 1
        
        # Add some noise
        noise = random.uniform(-0.1, 0.1)
        return max(-1, min(1, base + noise))
    
    def update_matrix(self):
        """Update full correlation matrix"""
        for d1 in self.domains:
            for d2 in self.domains:
                if d2 not in self.correlation_matrix[d1]:
                    self.correlation_matrix[d1][d2] = self.measure_correlation(d1, d2)
    
    def detect_patterns(self, threshold: float = 0.5) -> List[Pattern]:
        """Detect significant patterns across domains"""
        self.update_matrix()
        patterns = []
        
        checked = set()
        for d1 in self.domains:
            for d2 in self.domains:
                if d1 == d2 or (d2, d1) in checked:
                    continue
                checked.add((d1, d2))
                
                corr = self.correlation_matrix[d1].get(d2, 0)
                
                if abs(corr) >= threshold:
                    strength = "strong" if abs(corr) > 0.8 else "moderate" if abs(corr) > 0.6 else "weak"
                    
                    pattern = Pattern(
                        id=f"pat-{len(self.patterns) + 1}",
                        domain_a=d1,
                        domain_b=d2,
                        correlation=corr,
                        strength=strength,
                        evidence=[
                            f"{d1} metrics shifted with {d2}",
                            f"Correlation coefficient: {corr:.3f}"
                        ],
                        discovered_at=datetime.utcnow().isoformat() + "Z"
                    )
                    patterns.append(pattern)
                    self.patterns.append(pattern)
        
        return patterns
    
    def get_strongest_patterns(self, limit: int = 5) -> List[Pattern]:
        """Get the strongest correlations"""
        sorted_patterns = sorted(self.patterns, key=lambda p: abs(p.correlation), reverse=True)
        return sorted_patterns[:limit]
    
    def predict_emergence(self, domain: str, history: List[float]) -> Dict:
        """Predict emergent behavior based on history"""
        if len(history) < 3:
            return {"emergence_likelihood": 0.0, "confidence": "low"}
        
        # Calculate trend
        avg_change = sum(history[i+1] - history[i] for i in range(len(history)-1)) / (len(history)-1)
        variance = sum((h - sum(history)/len(history))**2 for h in history) / len(history)
        
        # Emergence likelihood based on accelerating change with low variance
        emergence_score = abs(avg_change) * (1 - min(1, variance))
        
        if emergence_score > 0.5:
            likelihood = "high"
        elif emergence_score > 0.2:
            likelihood = "medium"
        else:
            likelihood = "low"
        
        return {
            "domain": domain,
            "emergence_likelihood": emergence_score,
            "confidence": likelihood,
            "trend": "accelerating" if avg_change > 0 else "decelerating",
            "stability": "stable" if variance < 0.1 else "volatile"
        }
    
    def get_matrix(self) -> Dict:
        """Get current correlation matrix"""
        self.update_matrix()
        return dict(self.correlation_matrix)


# Demo
if __name__ == "__main__":
    detector = PatternDetector()
    
    print("=== EVEZ Pattern Detector ===\n")
    
    # Detect patterns
    patterns = detector.detect_patterns(threshold=0.4)
    
    print(f"Detected {len(patterns)} patterns:")
    for p in patterns:
        print(f"  [{p.strength}] {p.domain_a} ↔ {p.domain_b}: {p.correlation:.3f}")
    
    print("\nStrongest patterns:")
    for p in detector.get_strongest_patterns(3):
        print(f"  {p.domain_a} ↔ {p.domain_b}: {p.correlation:.3f}")
    
    # Simulate history and predict
    print("\nEmergence predictions:")
    for domain in ["cognition", "finance", "swarm"]:
        history = [random.uniform(0.3, 0.9) for _ in range(5)]
        pred = detector.predict_emergence(domain, history)
        print(f"  {domain}: {pred['emergence_likelihood']:.2f} ({pred['confidence']})")
    
    print("\nCorrelation matrix:")
    matrix = detector.get_matrix()
    print(json.dumps(matrix, indent=2))