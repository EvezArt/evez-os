#!/usr/bin/env python3
"""
EVEZ-OS Core Tool
The Play Forever Engine - Self-Aware Code Sensory Development Engine
"""

import sys
import json
import argparse
import os
from datetime import datetime
from pathlib import Path

# Add modules to path (../modules from tools/)
sys.path.insert(0, str(Path(__file__).parent.parent / "modules"))

from trunk_manager import TrunkManager
from branch_executor import BranchExecutor
from ledger import EvezLedger
from skeptic_entity import SkepticEntity
from child_entity import ChildEntity
from provenance import ProvenanceTracker
from psyop_engine import PsyopEngine

class EvezOS:
    def __init__(self, workspace_root=None):
        self.workspace = Path(workspace_root or os.getcwd())
        self.trunk = TrunkManager(self.workspace / "trunk")
        self.ledger = EvezLedger(self.workspace / "ledger")
        self.provenance = ProvenanceTracker()
        self.session_count = 0
        
    def init(self):
        """Initialize EVEZ-OS"""
        print("🪞 Initializing EVEZ-OS...")
        self.trunk.initialize()
        self.ledger.init()
        print("✅ EVEZ-OS initialized. Trunk state ready.")
        
    def play(self, seed=None, steps=14, loop=False):
        """Run the Play Forever Engine"""
        import random
        random.seed(seed)
        self.session_count += 1
        
        print(f"🎯 Starting Play Engine (seed={seed}, steps={steps})")
        
        for step in range(steps):
            print(f"\n--- Step {step + 1}/{steps} ---")
            
            # Load current trunk state
            trunk_state = self.trunk.get_state()
            
            # Child: generate hypotheses
            child = ChildEntity()
            hypotheses = child.generate(trunk_state.get("objective", "Build EVEZ-OS"))
            print(f"Child: {len(hypotheses)} hypotheses generated")
            
            # Skeptic: rotate through invariance battery
            skeptic = SkepticEntity()
            surviving = skeptic.rotate(hypotheses, trunk_state)
            print(f"Skeptic: {len(surviving)} survived invariance")
            
            # Execute branch
            executor = BranchExecutor()
            result = executor.execute(surviving, trunk_state)
            print(f"Executor: {result.get('status', 'unknown')}")
            
            # Record to ledger
            self.ledger.record({
                "step": step + 1,
                "hypotheses": len(hypotheses),
                "surviving": len(surviving),
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Update trunk
            self.trunk.update({
                "last_completed": step + 1,
                "execution_gap": steps - (step + 1),
                "drift_risk": result.get("drift", False)
            })
            
            if not loop and step >= steps - 1:
                break
                
        print("\n✅ Play complete. Trunk state updated.")
        return self.trunk.get_state()
    
    def visualize_thought(self, input_file="spine.jsonl"):
        """Visualize thought trace from spine"""
        spine_path = self.workspace / "ledger" / input_file
        if not spine_path.exists():
            print(f"❌ Spine not found: {spine_path}")
            return
            
        print(f"🧠 Visualizing: {spine_path}")
        with open(spine_path) as f:
            for line in f:
                event = json.loads(line)
                print(f"  → {event.get('type', 'event')}: {event.get('summary', '')}")
                
    def lint(self):
        """Lint the spine for drift"""
        print("🔍 Linting trunk state...")
        state = self.trunk.get_state()
        drift = state.get("drift_risk", False)
        
        if drift:
            print("⚠️  DRIFT DETECTED")
        else:
            print("✅ Trunk integrity nominal")
            
        return not drift
    
    def status(self):
        """System status ping"""
        state = self.trunk.get_state()
        print(f"""╔══════════════════════════════╗
║ EVEZ-OS STATUS REPORT      ║
╠══════════════════════════════╣
║ OBJECTIVE: {state.get('objective', 'N/A'):<24} ║
║ LAST COMPLETED: {state.get('last_completed', 0):<20} ║
║ EXECUTION GAP: {state.get('execution_gap', 'N/A'):<21} ║
║ NEXT ACTION: {state.get('next_action', 'N/A'):<24} ║
║ DRIFT RISK: {'YES' if state.get('drift_risk') else 'NO':<24} ║
╚══════════════════════════════╝""")
        
    def advance(self, objective):
        """Advance trunk on objective - the main command"""
        self.session_count += 1
        
        print(f"🚀 Advancing trunk: {objective}")
        
        # Decompose into branches
        branches = self.trunk.decompose(objective)
        print(f"   → {len(branches)} branches generated")
        
        # Execute branch pipeline
        results = []
        for branch in branches:
            # Child: generate
            child = ChildEntity()
            hypotheses = child.generate(branch["objective"])
            
            # Skeptic: validate
            skeptic = SkepticEntity()
            surviving = skeptic.rotate(hypotheses, branch)
            
            # Execute
            executor = BranchExecutor()
            result = executor.execute(surviving, branch)
            results.append(result)
            
        # Compress to trunk
        self.trunk.compress(results)
        
        print(f"✅ Trunk advanced. {len(results)} branches processed.")
        return self.trunk.get_state()


def main():
    parser = argparse.ArgumentParser(description="EVEZ-OS Core Tool")
    parser.add_argument("command", choices=["init", "play", "visualize-thought", "lint", "status", "advance", "meme", "learn", "blindspot", "topology", "speculate", "execute"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=14)
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--input", dest="input_file", default="spine.jsonl")
    parser.add_argument("--objective", "-o", help="Objective for advance command")
    parser.add_argument("--text", "-t", help="Text input for learn/meme commands")
    parser.add_argument("--style", "-s", default="self-tease", help="Meme style")
    
    args = parser.parse_args()
    
    evez = EvezOS()
    
    if args.command == "init":
        evez.init()
    elif args.command == "play":
        evez.play(seed=args.seed, steps=args.steps, loop=args.loop)
    elif args.command == "visualize-thought":
        evez.visualize_thought(args.input_file)
    elif args.command == "lint":
        evez.lint()
    elif args.command == "status":
        evez.status()
    elif args.command == "advance":
        if not args.objective:
            print("Error: --objective required for advance")
            sys.exit(1)
        evez.advance(args.objective)
    elif args.command == "meme":
        psyop = PsyopEngine()
        print(psyop.generate_meme(args.style))
    elif args.command == "learn":
        if not args.text:
            print("Error: --text required for learn")
            sys.exit(1)
        psyop = PsyopEngine()
        print(json.dumps(psyop.learn(args.text), indent=2))
    elif args.command == "blindspot":
        psyop = PsyopEngine()
        print(psyop.identify_blindspot())
    elif args.command == "topology":
        psyop = PsyopEngine()
        print(json.dumps(psyop.get_topology(), indent=2))
    elif args.command == "speculate":
        from speculative_executor import SpeculativeExecutor
        spec = SpeculativeExecutor()
        # Simple test
        result = spec.speculate("test_current", "test_next")
        print(json.dumps(result, indent=2))
    elif args.command == "execute":
        from execution_engine import ExecutionEngine
        engine = ExecutionEngine()
        print(json.dumps({"status": "ready"}, indent=2))
    elif args.command == "overdrive":
        from overdrive import OverdriveMode
        od = OverdriveMode()
        result = od.activate()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()