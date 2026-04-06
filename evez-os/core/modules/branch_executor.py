"""
EVEZ-OS Branch Executor
Executes branch logic from Child → Skeptic → Sandbox pipeline
"""

import json
import random

class BranchExecutor:
    def __init__(self):
        self.execution_count = 0
        
    def execute(self, hypotheses, branch_context):
        """Execute branch with surviving hypotheses"""
        self.execution_count += 1
        
        if not hypotheses:
            return {
                "status": "no_hypotheses",
                "output": {},
                "drift": False
            }
            
        # Select winner (highest combined score)
        winner = max(hypotheses, key=lambda h: h.get("score", 0))
        
        # Simulate execution (in real impl, would run actual code)
        result = {
            "branch_id": branch_context.get("id", "unknown"),
            "winner": winner.get("text", ""),
            "score": winner.get("score", 0),
            "status": "success",
            "output": {
                "hypotheses_tested": len(hypotheses),
                "winning_hypothesis": winner.get("text", "")[:100],
                "confidence": "high" if winner.get("score", 0) > 7 else "med"
            },
            "drift": self._check_drift(winner, branch_context)
        }
        
        return result
        
    def _check_drift(self, hypothesis, context):
        """Check for drift from trunk objective"""
        obj = context.get("objective", "")
        hyp = hypothesis.get("text", "")
        
        # Simple keyword drift check
        obj_keywords = set(obj.lower().split()) - {"the", "a", "an", "for", "on"}
        hyp_keywords = set(hyp.lower().split()) - {"the", "a", "an", "for", "on"}
        
        overlap = len(obj_keywords & hyp_keywords) / max(len(obj_keywords), 1)
        return overlap < 0.3  # Flag if < 30% keyword overlap