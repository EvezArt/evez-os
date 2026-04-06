"""
EVEZ Child Entity
Generates 5 hypotheses - from obvious to unexpected
"""

import random

class ChildEntity:
    def __init__(self):
        self.entity_type = "child"
        
    def generate(self, objective, count=5):
        """Generate hypotheses for objective"""
        hypotheses = []
        
        # Generate variations from obvious to creative
        templates = [
            f"Standard approach: {objective}",
            f"Refined approach: {objective}",
            f"Alternative: {objective}",
            f"Non-obvious: {objective}",
            f"Wildcard: {objective}"
        ]
        
        for i, template in enumerate(templates[:count]):
            novelty = 5 - i  # First is most obvious
            feasibility = random.randint(3, 5) if i < 3 else random.randint(2, 4)
            
            hypotheses.append({
                "id": f"h{i+1}",
                "text": template,
                "novelty": novelty,
                "feasibility": feasibility,
                "score": novelty + feasibility,
                "rank": i + 1
            })
            
        # Sort by combined score
        hypotheses.sort(key=lambda h: h["score"], reverse=True)
        
        return hypotheses
        
    def field_report(self, system_state):
        """Narrate system state as field report"""
        return {
            "perceives": "System active, processing input signals",
            "learning": "Adapting to trunk decomposition patterns",
            "uncertain": "Seeking first landed transaction for anchor"
        }