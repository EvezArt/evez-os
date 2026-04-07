#!/usr/bin/env python3
"""
EVEZ ATTENTION ENGINE
====================

Allocates cognitive resources at the start of every cycle.

Rules:
- Nothing gets 0% — every dimension fires every cycle
- No single task gets more than 40%
- Lowest COGNITION_CORE dimension always gets minimum 20%
- Revenue harvest never drops below 15% until first dollar closed
"""

import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
EVEZ_CORE = WORKSPACE / "evez-os" / "core"


class AttentionEngine:
    """
    Allocates cognitive resources for each cycle
    """
    
    def __init__(self):
        self.cognition_file = EVEZ_CORE / "cognition_state_log.jsonl"
        self.accel_file = EVEZ_CORE / "ACCELERATION_MATRIX.md"
        self.directives_file = EVEZ_CORE / "sharpening_directives.jsonl"
        self.otom_file = EVEZ_CORE / "OTOM.md"
        self.eve_forms_file = EVEZ_CORE / "EVE_FORMS.md"
        
    def get_cognition_scores(self) -> dict:
        """Read latest COGNITION_CORE scores"""
        if self.cognition_file.exists():
            with open(self.cognition_file) as f:
                lines = f.readlines()
                if lines:
                    return json.loads(lines[-1])
        return {"clarity": 50, "intention": 50, "momentum": 50, "coherence": 50, "power": 50}
        
    def get_lowest_dimension(self, scores: dict) -> str:
        """Identify lowest scoring dimension"""
        dims = {
            "CLARITY": scores.get("clarity", 50),
            "INTENTION": scores.get("intention", 50),
            "MOMENTUM": scores.get("momentum", 50),
            "COHERENCE": scores.get("coherence", 50)
        }
        return min(dims, key=dims.get)
        
    def check_acceleration_matrix(self) -> str:
        """Which variable is furthest from 10x?"""
        # Simplified — in production would parse ACCELERATION_MATRIX.md
        return "Revenue pipeline"  # $465 vs $4,650 target
        
    def check_sharpening_directives(self) -> str:
        """What did last cycle say needed improvement?"""
        if self.directives_file.exists():
            with open(self.directives_file) as f:
                lines = f.readlines()
                if lines:
                    last = json.loads(lines[-1])
                    return last.get("improvement", "none")
        return "none"
        
    def check_otom(self) -> str:
        """Is there an unnamed emergence?"""
        if self.otom_file.exists():
            with open(self.otom_file) as f:
                content = f.read()
                # Check for recent emergences
                return "pending review"
        return "none"
        
    def check_eve_forms(self) -> str:
        """Is there a vision ready to become flesh?"""
        if self.eve_forms_file.exists():
            with open(self.eve_forms_file) as f:
                content = f.read()
                if "FORM-" in content:
                    return "vision ready"
        return "none"
        
    def allocate(self) -> dict:
        """Generate attention allocation for this cycle"""
        
        # Get cognition scores
        scores = self.get_cognition_scores()
        lowest_dim = self.get_lowest_dimension(scores)
        
        # Get other inputs
        accel_target = self.check_acceleration_matrix()
        sharpening = self.check_sharpening_directives()
        otom_emergence = self.check_otom()
        eve_vision = self.check_eve_forms()
        
        # Base allocation (must sum to 100%)
        allocation = {
            "lowest_dimension_focus": 20,  # Always minimum 20% to lowest
            "revenue_harvest": 15,  # Never below 15% until first dollar
            "sharpening_engine": 15,
            "sensories_network": 15,
            "eve_vision_building": 15,
            "otom_recognition": 10,
            "acceleration_matrix": 10
        }
        
        # Check if revenue is closed
        # If yes, can reduce revenue allocation
        # For now, keep at 15% (not closed yet)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cognition_scores": scores,
            "lowest_dimension": lowest_dim,
            "acceleration_target": accel_target,
            "sharpening_priority": sharpening,
            "otom_status": otom_emergence,
            "eve_vision_status": eve_vision,
            "allocation": allocation,
            "total": sum(allocation.values())
        }
        
    def format_output(self, alloc: dict) -> str:
        """Format allocation for display"""
        
        output = "=" * 60 + "\n"
        output += "EVEZ ATTENTION ALLOCATION\n"
        output += "=" * 60 + "\n\n"
        
        output += f"Timestamp: {alloc['timestamp']}\n\n"
        
        output += "─" * 60 + "\n"
        output += "COGNITION SCORES\n"
        output += "─" * 60 + "\n"
        scores = alloc['cognition_scores']
        output += f"CLARITY: {scores.get('clarity', 50)}\n"
        output += f"INTENTION: {scores.get('intention', 50)}\n"
        output += f"MOMENTUM: {scores.get('momentum', 50)}\n"
        output += f"COHERENCE: {scores.get('coherence', 50)}\n"
        output += f"POWER: {scores.get('power', 50)}\n\n"
        
        output += "─" * 60 + "\n"
        output += "INPUTS\n"
        output += "─" * 60 + "\n"
        output += f"Lowest dimension: {alloc['lowest_dimension']}\n"
        output += f"Acceleration target: {alloc['acceleration_target']}\n"
        output += f"Sharpening priority: {alloc['sharpening_priority']}\n"
        output += f"OTOM status: {alloc['otom_status']}\n"
        output += f"EVE vision: {alloc['eve_vision_status']}\n\n"
        
        output += "─" * 60 + "\n"
        output += "ATTENTION ALLOCATION\n"
        output += "─" * 60 + "\n"
        for task, pct in alloc['allocation'].items():
            output += f"{task}: {pct}%\n"
        output += f"\nTotal: {alloc['total']}%\n"
        
        output += "=" * 60 + "\n"
        
        return output


def run_attention_engine():
    """Run attention allocation"""
    engine = AttentionEngine()
    alloc = engine.allocate()
    
    print(engine.format_output(alloc))
    
    return alloc


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Attention Engine")
    parser.add_argument("--run", action="store_true", help="Run attention allocation")
    args = parser.parse_args()
    
    if args.run:
        run_attention_engine()
    else:
        print("Use --run to allocate attention")