#!/usr/bin/env python3
"""
EVEZ OS Continuous Build Loop
Runs every 15 minutes — reads state, executes highest priority, commits, updates dashboard
"""

import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

WORKSPACE = Path("/root/.openclaw/workspace")
EVEZ_CORE = WORKSPACE / "evez-os" / "core"

class ContinuousBuildLoop:
    """
    Autonomous loop that:
    1. Reads current EVEZ OS state
    2. Identifies highest priority incomplete item
    3. Executes it
    4. Commits result
    5. Logs cycle
    """
    
    def __init__(self):
        self.cycle = 0
        self.log_file = EVEZ_CORE / "continuous_loop_log.jsonl"
        self.state_file = EVEZ_CORE / "loop_state.json"
        
    def log(self, entry: dict):
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
    def get_system_state(self) -> dict:
        """Read current EVEZ OS state"""
        # Read ledger
        ledger_count = 0
        if (EVEZ_CORE / "ledger" / "spine.jsonl").exists():
            with open(EVEZ_CORE / "ledger" / "spine.jsonl") as f:
                ledger_count = sum(1 for _ in f)
                
        # Read context
        context_count = 0
        if (EVEZ_CORE / "context.jsonl").exists():
            with open(EVEZ_CORE / "context.jsonl") as f:
                context_count = sum(1 for _ in f)
                
        # Read current objective
        objective = "Execute first harvest"
        if (EVEZ_CORE / "trunk" / "state.json").exists():
            try:
                with open(EVEZ_CORE / "trunk" / "state.json") as f:
                    state = json.load(f)
                    objective = state.get("objective", objective)
            except:
                pass
                
        return {
            "ledger_events": ledger_count,
            "context_entries": context_count,
            "current_objective": objective,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def identify_next_action(self, state: dict) -> dict:
        """Identify highest priority incomplete item"""
        # Priority queue based on system state
        actions = [
            {"priority": 1, "action": "run_harvest_cycle", "reason": "Continue toward revenue"},
            {"priority": 2, "action": "update_dashboard", "reason": "Maintain monitoring"},
            {"priority": 3, "action": "push_to_github", "reason": "Sync state"},
            {"priority": 4, "action": "scan_opportunities", "reason": "Find new revenue"}
        ]
        
        return actions[0]  # Always pick highest priority
        
    def execute_action(self, action: dict) -> dict:
        """Execute the identified action"""
        action_type = action["action"]
        
        if action_type == "run_harvest_cycle":
            # Run EVEZ cycle
            result = subprocess.run(
                ["python3", "tools/evez.py", "play", "--steps", "1"],
                cwd=str(EVEZ_CORE),
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "executed": action_type,
                "success": result.returncode == 0,
                "output": result.stdout[:200]
            }
            
        elif action_type == "update_dashboard":
            # Update loop state
            state = self.get_system_state()
            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=2)
            return {
                "executed": action_type,
                "success": True,
                "output": f"State updated: {state['ledger_events']} events"
            }
            
        elif action_type == "push_to_github":
            # Git commit and push
            result = subprocess.run(
                ["git", "add", "-A"],
                cwd=str(WORKSPACE),
                capture_output=True,
                text=True
            )
            result = subprocess.run(
                ["git", "commit", "-m", f"EVEZ continuous loop cycle {self.cycle}"],
                cwd=str(WORKSPACE),
                capture_output=True,
                text=True
            )
            result = subprocess.run(
                ["git", "push", "origin", "master"],
                cwd=str(WORKSPACE),
                capture_output=True,
                text=True
            )
            return {
                "executed": action_type,
                "success": result.returncode == 0,
                "output": "Pushed to GitHub"
            }
            
        else:
            return {
                "executed": action_type,
                "success": False,
                "output": "Unknown action"
            }
            
    def run_cycle(self) -> dict:
        """Run one complete build loop cycle"""
        self.cycle += 1
        cycle_start = datetime.utcnow().isoformat()
        
        # Get state
        state = self.get_system_state()
        
        # Identify next action
        next_action = self.identify_next_action(state)
        
        # Execute
        result = self.execute_action(next_action)
        
        # Log
        cycle_log = {
            "cycle": self.cycle,
            "start": cycle_start,
            "state": state,
            "action": next_action,
            "result": result,
            "end": datetime.utcnow().isoformat()
        }
        
        self.log(cycle_log)
        
        return cycle_log
        
    def get_status(self) -> dict:
        """Get current loop status for monitoring"""
        cycles = []
        if self.log_file.exists():
            with open(self.log_file) as f:
                for line in f:
                    cycles.append(json.loads(line))
                    
        return {
            "running": True,
            "current_cycle": self.cycle,
            "total_cycles": len(cycles),
            "last_cycle": cycles[-1] if cycles else None,
            "next_scheduled": "15 minutes"
        }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Continuous Build Loop")
    parser.add_argument("--run", action="store_true", help="Run one cycle")
    parser.add_argument("--status", action="store_true", help="Get status")
    parser.add_argument("--watch", action="store_true", help="Run continuously")
    args = parser.parse_args()
    
    loop = ContinuousBuildLoop()
    
    if args.status:
        print(json.dumps(loop.get_status(), indent=2))
    elif args.run:
        result = loop.run_cycle()
        print(f"Cycle {result['cycle']} complete: {result['result']['executed']}")
    elif args.watch:
        print("Starting continuous loop (Ctrl+C to stop)...")
        while True:
            result = loop.run_cycle()
            print(f"[{datetime.now().isoformat()}] Cycle {result['cycle']}: {result['result']['executed']}")
            time.sleep(900)  # 15 minutes
    else:
        print("Use --run, --status, or --watch")