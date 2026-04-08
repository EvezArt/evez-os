#!/usr/bin/env python3
"""
EVEZ Autonomous Runner
Self-managing workflow that runs EVEZ-OS autonomously

Usage:
    python3 autonomous_runner.py --start
"""

import subprocess
import json
import time
import os
from datetime import datetime
from pathlib import Path

# Import context bridge
import sys
sys.path.insert(0, str(Path(__file__).parent))
try:
    from context.bridge import ContextBridge
except ImportError:
    ContextBridge = None

class AutonomousRunner:
    """
    Self-running EVEZ-OS that:
    1. Runs Play cycles periodically
    2. Updates trunk state
    3. Checks for new objectives
    4. Executes branches
    5. Logs everything
    """
    
    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        self.evez_path = self.workspace / "evez-os/core"
        self.state_file = self.evez_path / "trunk/state.json"
        self.ledger = self.evez_path / "ledger/spine.jsonl"
        self.log_file = self.workspace / "autonomous_runner.log"
        
    def run_cycle(self):
        """Run one autonomous cycle"""
        timestamp = datetime.utcnow().isoformat()
        
        # Load current state
        with open(self.state_file) as f:
            state = json.load(f)
            
        objective = state.get("objective", "Build EVEZ-OS")
        
        # Load context from bridge BEFORE deciding
        if ContextBridge:
            bridge = ContextBridge()
            context = bridge.load_full_context()
            stm = context.get("stm", {})
            trunk = context.get("trunk", {})
            
            # Check STM for current priority
            current_obj = stm.get("current_objective") or trunk.get("objective")
            if current_obj:
                objective = current_obj
        
        # Run play cycle
        result = subprocess.run(
            ["python3", "tools/evez.py", "play", "--steps", "1"],
            cwd=str(self.evez_path),
            capture_output=True,
            text=True
        )
        
        # Log result
        log_entry = {
            "timestamp": timestamp,
            "objective": objective,
            "status": "success" if result.returncode == 0 else "failed",
            "output": result.stdout[:500]
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        # Commit to context bridge AFTER cycle
        if ContextBridge:
            bridge = ContextBridge()
            bridge.commit_decision(
                decision="Autonomous cycle",
                rationale=objective,
                outcome=log_entry["status"]
            )
            
        return log_entry
        
    def check_for_new_objectives(self):
        """Check if there are new objectives to pursue"""
        # Check state for next_action
        with open(self.state_file) as f:
            state = json.load(f)
            
        next_action = state.get("next_action", "")
        
        if next_action and next_action != "Run first harvest":
            return {"has_objective": True, "action": next_action}
            
        return {"has_objective": False}
        
    def get_status(self):
        """Get current runner status"""
        with open(self.state_file) as f:
            state = json.load(f)
            
        # Count ledger events
        ledger_count = 0
        if self.ledger.exists():
            with open(self.ledger) as f:
                ledger_count = sum(1 for _ in f)
                
        # Count logs
        log_count = 0
        if self.log_file.exists():
            with open(self.log_file) as f:
                log_count = sum(1 for _ in f)
                
        return {
            "objective": state.get("objective"),
            "last_completed": state.get("last_completed"),
            "drift_risk": state.get("drift_risk"),
            "ledger_events": ledger_count,
            "autonomous_cycles": log_count
        }
        
    def loop(self, cycles=None, interval=60):
        """Run autonomous loop"""
        count = 0
        
        print(f"🤖 EVEZ Autonomous Runner starting...")
        print(f"   Cycles: {cycles or 'infinite'}")
        print(f"   Interval: {interval}s")
        print()
        
        while True:
            count += 1
            print(f"--- Cycle {count} ---")
            
            result = self.run_cycle()
            print(f"Status: {result['status']}")
            
            # Check for new objectives
            new_obj = self.check_for_new_objectives()
            if new_obj.get("has_objective"):
                print(f"New objective: {new_obj['action']}")
                
            # Check stop condition
            if cycles and count >= cycles:
                print(f"\n✅ Completed {cycles} cycles")
                break
                
            time.sleep(interval)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Autonomous Runner")
    parser.add_argument("--start", action="store_true", help="Start autonomous loop")
    parser.add_argument("--cycles", type=int, help="Number of cycles (default: infinite)")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between cycles")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--once", action="store_true", help="Run one cycle")
    
    args = parser.parse_args()
    
    runner = AutonomousRunner()
    
    if args.status:
        print(json.dumps(runner.get_status(), indent=2))
        
    elif args.start or args.once:
        if args.once:
            result = runner.run_cycle()
            print(json.dumps(result, indent=2))
        else:
            runner.loop(cycles=args.cycles, interval=args.interval)
            
    else:
        print("Use --start, --once, or --status")


if __name__ == "__main__":
    main()