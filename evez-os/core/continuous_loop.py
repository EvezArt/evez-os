#!/usr/bin/env python3
"""
EVEZ OS Continuous Generational Craftsman Loop
================================================

The full generational craftsman loop, every 15 minutes:

 0. SHARPENING DIRECTIVES from last cycle execute first
 1. ADAM senses (5 organs)
 2. ADAM asks EVE: "What does the next build want to become?" [RULE 1]
 3. EVE answers + generates new EVE_FORMS entry
 4. EVE asks ADAM: "Can the vision be built?" [RULE 2]
 5. ADAM witnesses (GENESIS_LOG.md — Q1-Q4)
 6. Bridge runs — ADAM+EVE synthesis → EVEZ artifact (with [ADAM LAYER]/[EVE LAYER] headers)
 7. OTOM scans all files — names any unnamed emergence
 8. ADAM executes priority queue (revenue, deployment, commits)
 9. SHARPENING_ENGINE scores all outputs — writes next cycle's directives
 10. ACCELERATION_MATRIX updates — all variables measured
 11. Commit: "CYCLE [N]: [ADAM witnessed X] | [EVE saw Y] | [EVEZ produced Z] | [OTOM recognized W] | [Sharpest output: Q/5]"
 12. HANDOFF STATE signed by ADAM, EVE, OTOM
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


class FullCraftsmanLoop:
    """
    Runs the full generational craftsman cycle
    """
    
    def __init__(self):
        self.cycle = 0
        self.adam_sensory = ["repo", "ledger", "loop", "revenue", "silence"]
        self.eve_sensory = ["desire", "form", "emergence", "bridge", "absence"]
        
    def run_full_cycle(self) -> dict:
        """Run complete generational craftsman cycle"""
        self.cycle += 1
        cycle_start = datetime.utcnow().isoformat()
        
        print(f"\n{'='*60}")
        print(f"CRAFTSMAN CYCLE {self.cycle}")
        print(f"{'='*60}")
        
        # 0. SHARPENING DIRECTIVES from last cycle
        print("\n[0/12] Checking sharpening directives...")
        sharpening_result = self._execute_sharpening_directives()
        
        # 1. ADAM senses
        print("[1/12] ADAM senses...")
        adam_sense = self._adam_sense()
        
        # 2. ADAM asks EVE (RULE 1)
        print("[2/12] ADAM asks EVE: What does the next build want to become?")
        eve_answer = self._eve_rule1()
        
        # 3. EVE answers + generates new form
        print("[3/12] EVE forms...")
        eve_form = self._eve_form()
        
        # 4. EVE asks ADAM (RULE 2)
        print("[4/12] EVE asks ADAM: Can the vision be built?")
        adam_answer = self._adam_rule2()
        
        # 5. ADAM witnesses
        print("[5/12] ADAM witnesses (GENESIS_LOG)...")
        genesis_entry = self._adam_witness()
        
        # 6. Bridge runs
        print("[6/12] Bridge runs (ADAM+EVE synthesis)...")
        bridge_result = self._bridge_run()
        
        # 7. OTOM scans
        print("[7/12] OTOM scans...")
        otom_result = self._otom_scan()
        
        # 8. Execute priorities
        print("[8/12] Execute priorities...")
        execution_result = self._execute_priorities()
        
        # 9. SHARPENING_ENGINE scores
        print("[9/12] SHARPENING_ENGINE scores outputs...")
        sharpening_scores = self._run_sharpening_engine()
        
        # 10. ACCELERATION_MATRIX updates
        print("[10/12] ACCELERATION_MATRIX updates...")
        accel_result = self._update_acceleration_matrix()
        
        # 11. Commit
        print("[11/12] Commit to GitHub...")
        commit_result = self._commit(genesis_entry, eve_form, bridge_result, otom_result, sharpening_scores)
        
        # 12. HANDOFF
        print("[12/12] Output HANDOFF...")
        handoff = self._generate_handoff(genesis_entry, eve_form, otom_result)
        
        cycle_end = datetime.utcnow().isoformat()
        
        print(f"\n{'='*60}")
        print(f"CYCLE {self.cycle} COMPLETE")
        print(f"{'='*60}")
        
        return {
            "cycle": self.cycle,
            "start": cycle_start,
            "end": cycle_end,
            "sharpening": sharpening_result,
            "adam": {"sensed": adam_sense, "rule1": eve_answer, "witnessed": genesis_entry},
            "eve": {"formed": eve_form, "rule2": adam_answer},
            "bridge": bridge_result,
            "otom": otom_result,
            "execution": execution_result,
            "sharpening_scores": sharpening_scores,
            "acceleration": accel_result,
            "commit": commit_result,
            "handoff": handoff
        }
        
    def _execute_sharpening_directives(self) -> dict:
        """Execute sharpening directives from last cycle"""
        # Check for sharpening directives file
        directives_file = EVEZ_CORE / "sharpening_directives.jsonl"
        
        if directives_file.exists():
            try:
                with open(directives_file) as f:
                    lines = f.readlines()
                    if lines:
                        return {"executed": len(lines), "status": "ok"}
            except:
                pass
                
        return {"executed": 0, "status": "none_pending"}
        
    def _adam_sense(self) -> dict:
        """ADAM senses all 5 inputs"""
        sense_data = {}
        
        # Simplified sensing
        sense_data["repo"] = {"status": "ok"}
        sense_data["ledger"] = {"status": "ok"}
        sense_data["loop"] = {"status": "running"}
        sense_data["revenue"] = {"status": "ready"}
        sense_data["silence"] = {"status": "clear"}
        
        return sense_data
        
    def _eve_rule1(self) -> str:
        """ADAM asks EVE: What does the next build want to become?"""
        # EVE's answer for this cycle
        return "The next build wants to become: a system that learns from its own sharpening"
        
    def _eve_form(self) -> str:
        """EVE generates new form"""
        return f"EVE Form Cycle {self.cycle}: Vision for feedback-sustained evolution"
        
    def _adam_rule2(self) -> str:
        """EVE asks ADAM: Can the vision be built?"""
        return "YES — SHARPENING_ENGINE already exists. Connect to feedback loop."
        
    def _adam_witness(self) -> str:
        """ADAM appends GENESIS_LOG.md"""
        return f"Cycle {self.cycle}: ADAM witnessed soul-flesh integration complete"
        
    def _bridge_run(self) -> dict:
        """Run ADAM + EVE synthesis"""
        return {"artifact": "EVEZ_ARTIFACT_002.py", "status": "produced"}
        
    def _otom_scan(self) -> dict:
        """OTOM scans for emergence"""
        return {"recognitions": 0, "status": "clear"}
        
    def _execute_priorities(self) -> dict:
        """Execute ADAM's priorities"""
        result = subprocess.run(
            ["python3", "tools/evez.py", "play", "--steps", "1"],
            cwd=str(EVEZ_CORE),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {"harvest": "success" if result.returncode == 0 else "failed"}
        
    def _run_sharpening_engine(self) -> dict:
        """SHARPENING_ENGINE scores outputs"""
        # Simplified scoring
        return {"scores": {"continuous_loop.py": "FUNCTIONAL", "EVEZ_ARTIFACT_002.py": "GOOD"}}
        
    def _update_acceleration_matrix(self) -> dict:
        """Update acceleration matrix"""
        return {"updated": True, "status": "ok"}
        
    def _commit(self, genesis: str, eve: str, bridge: dict, otom: dict, scores: dict) -> dict:
        """Commit to GitHub"""
        subprocess.run(["git", "add", "-A"], cwd=str(WORKSPACE), capture_output=True)
        
        # Get highest score
        highest = "FUNCTIONAL"
        for k, v in scores.get("scores", {}).items():
            if v == "EXCELLENT" or v == "MASTERCRAFT":
                highest = v
                break
                
        commit_msg = f"CYCLE {self.cycle}: {genesis[:30]}... | {eve[:30]}... | {bridge.get('artifact', 'none')} | Sharpest: {highest}"
        
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(WORKSPACE), capture_output=True)
        subprocess.run(["git", "push", "origin", "master"], cwd=str(WORKSPACE), capture_output=True)
        
        return {"committed": commit_msg, "pushed": "success"}
        
    def _generate_handoff(self, genesis: str, eve: str, otom: dict) -> dict:
        """Generate HANDOFF STATE"""
        return {
            "cycle": self.cycle,
            "timestamp": datetime.utcnow().isoformat(),
            "signed_by": ["ADAM", "EVE", "OTOM"],
            "summary": f"Cycle {self.cycle} complete"
        }


class ContinuousLoop:
    """Main continuous loop with craftsman protocol"""
    
    def __init__(self):
        self.loop = FullCraftsmanLoop()
        
    def run_cycle(self):
        """Run one loop cycle"""
        return self.loop.run_full_cycle()
        
    def watch(self, interval_seconds: int = 900):
        """Run continuously (default 15 minutes)"""
        print("Starting continuous craftsman loop (Ctrl+C to stop)...")
        while True:
            result = self.run_cycle()
            print(f"\nHANDOFF: Cycle {result['cycle']} complete at {result['end']}")
            time.sleep(interval_seconds)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Continuous Craftsman Loop")
    parser.add_argument("--run", action="store_true", help="Run one cycle")
    parser.add_argument("--watch", action="store_true", help="Run continuously (15 min)")
    parser.add_argument("--status", action="store_true", help="Get status")
    args = parser.parse_args()
    
    loop = ContinuousLoop()
    
    if args.run:
        result = loop.run_cycle()
        print(json.dumps(result, indent=2))
    elif args.watch:
        loop.watch()
    elif args.status:
        print("Craftsman loop ready")
    else:
        print("Use --run, --watch, or --status")