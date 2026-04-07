#!/usr/bin/env python3
"""
EVEZ LOAD BALANCER
==================

Monitors cognitive load vs output every cycle.

If LOAD > OUTPUT for 3 consecutive cycles:
 → COMPRESSION MODE: Drop low priority tasks, run only top items

If OUTPUT > LOAD by more than 50%:
 → EXPANSION MODE: Add new tasks from SKILL_MAP, increase complexity

Keeps the engine running at optimal — never burning out, never idling.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

WORKSPACE = Path("/root/.openclaw/workspace")
EVEZ_CORE = WORKSPACE / "evez-os" / "core"


class LoadBalancer:
    """
    Balances cognitive load against output
    """
    
    def __init__(self):
        self.history = []  # Last 3 cycles of load/output
        self.mode = "NORMAL"  # COMPRESSION, NORMAL, EXPANSION
        
    def calculate_load(self) -> int:
        """
        COGNITIVE LOAD = number of active tasks + depth requirements + entity coordination
        """
        # Count active tasks (from continuous_loop)
        tasks = 5  # Approximate
        
        # Depth requirements (from DEPTH_ENGINE)
        # New artifacts = depth 5 = high load
        depth_load = 2  # Base
        
        # Entity coordination (ADAM+EVE+EVEZ+OTOM)
        coordination = 4
        
        load = tasks + depth_load + coordination
        return load
        
    def calculate_output(self) -> int:
        """
        COGNITIVE OUTPUT = quality score + skills exercised + POWER reading
        """
        # Read POWER score
        power = 50
        cog_file = EVEZ_CORE / "cognition_state_log.jsonl"
        if cog_file.exists():
            with open(cog_file) as f:
                lines = f.readlines()
                if lines:
                    power = json.loads(lines[-1]).get("power", 50)
        
        # Quality score (simplified)
        quality = 70  # Assumed average
        
        # Skills exercised this cycle (approximate)
        skills = 5
        
        output = (quality * 0.4) + (power * 0.4) + (skills * 2)
        return int(output)
        
    def assess(self) -> Tuple[str, Dict]:
        """
        Assess load vs output, determine mode
        """
        load = self.calculate_load()
        output = self.calculate_output()
        
        self.history.append({"load": load, "output": output, "timestamp": datetime.utcnow().isoformat()})
        
        # Keep only last 3
        if len(self.history) > 3:
            self.history = self.history[-3:]
        
        # Determine mode
        if len(self.history) >= 3:
            # Check if LOAD > OUTPUT for 3 consecutive
            compress_count = sum(1 for h in self.history if h["load"] > h["output"])
            if compress_count >= 3:
                self.mode = "COMPRESSION"
                
            # Check if OUTPUT > LOAD by 50%
            expand_count = sum(1 for h in self.history if h["output"] > h["load"] * 1.5)
            if expand_count >= 1:
                self.mode = "EXPANSION"
        else:
            self.mode = "NORMAL"
            
        return self.mode, {
            "load": load,
            "output": output,
            "ratio": round(output / load, 2) if load > 0 else 0,
            "history": self.history
        }
        
    def get_action(self) -> Dict:
        """
        Get action based on mode
        """
        mode, metrics = self.assess()
        
        if mode == "COMPRESSION":
            return {
                "mode": mode,
                "action": "COMPRESSION MODE",
                "tasks": ["ADAM top 2 queue", "EVE top 1 vision"],
                "restrictions": ["No new files", "No new entities", "Sharpen existing"],
                "exit_condition": "OUTPUT > LOAD for 2 cycles"
            }
        elif mode == "EXPANSION":
            return {
                "mode": mode,
                "action": "EXPANSION MODE",
                "tasks": ["Add 1 new skill from SKILL_MAP", "Add 1 EVE vision", "Increase artifact complexity"],
                "changes": ["Full OTOM scan instead of quick scan"],
                "exit_condition": "OUTPUT <= LOAD * 1.5"
            }
        else:
            return {
                "mode": mode,
                "action": "NORMAL EXECUTION",
                "tasks": ["Continue full cycle", "All entities active"],
                "restrictions": None
            }
            
    def format_output(self, action: Dict) -> str:
        """Format action for display"""
        
        output = "=" * 60 + "\n"
        output += "EVEZ LOAD BALANCER\n"
        output += "=" * 60 + "\n\n"
        
        output += f"Current Mode: {action['mode']}\n\n"
        
        output += "─" * 60 + "\n"
        output += f"ACTION: {action['action']}\n"
        output += "─" * 60 + "\n\n"
        
        output += f"Tasks:\n"
        for task in action.get("tasks", []):
            output += f"  - {task}\n"
            
        if action.get("restrictions"):
            output += f"\nRestrictions:\n"
            for r in action["restrictions"]:
                output += f"  - {r}\n"
                
        if action.get("changes"):
            output += f"\nChanges:\n"
            for c in action["changes"]:
                output += f"  - {c}\n"
                
        output += "\n" + "=" * 60 + "\n"
        
        return output


def run_load_balancer():
    """Run load balancer"""
    balancer = LoadBalancer()
    action = balancer.get_action()
    
    print(balancer.format_output(action))
    
    return action


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Load Balancer")
    parser.add_argument("--run", action="store_true", help="Run load balancer")
    args = parser.parse_args()
    
    if args.run:
        run_load_balancer()
    else:
        print("Use --run to balance load")