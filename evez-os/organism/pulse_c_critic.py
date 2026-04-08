#!/usr/bin/env python3
"""
Pulse C: Critic
Logs learnings and updates trunk
Runs every 60 min
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
STATE_FILE = WORKSPACE / "evez-os/organism/organism_state.json"
LEDGER_FILE = WORKSPACE / "octoklaw/LEDGER.md"

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"error": "no_state"}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def log_ledger(entry):
    with open(LEDGER_FILE, "a") as f:
        f.write(f"\n## {datetime.utcnow().isoformat()} - Pulse C (Critic)\n{entry}\n")

def run_critic():
    print("[PULSE C] Running Critic...")
    
    state = load_state()
    if "error" in state:
        print("[PULSE C] No state - initializing")
        state = {"pulse_state": {}}
    
    # Generate learnings from this cycle
    learnings = []
    
    # Check what happened
    if state.get("last_harvest_result"):
        learnings.append({
            "cycle": state.get("pulse_state", {}).get("cycle_count", 1),
            "learning": f"Harvest produced: {state['last_harvest_result']['action_proposed']}",
            "source": "harvest"
        })
    
    if state.get("last_hypothesis_batch"):
        learnings.append({
            "cycle": state.get("pulse_state", {}).get("cycle_count", 1),
            "learning": f"Explorer generated {len(state['last_hypothesis_batch'])} hypotheses",
            "source": "explore"
        })
    
    # Check for missing capabilities
    if state.get("open_missing_capabilities"):
        learnings.append({
            "cycle": state.get("pulse_state", {}).get("cycle_count", 1),
            "learning": f"Open blockers: {len(state['open_missing_capabilities'])}",
            "source": "system"
        })
    
    # If nothing happened, add a learning anyway
    if not learnings:
        learnings.append({
            "cycle": state.get("pulse_state", {}).get("cycle_count", 1),
            "learning": "Cycle ran with no new data - system stable",
            "source": "system"
        })
    
    # Update state with learnings
    current_learnings = state.get("top_learnings", [])
    state["top_learnings"] = (learnings + current_learnings)[:5]  # Keep last 5
    
    # Increment cycle count
    if "pulse_state" not in state:
        state["pulse_state"] = {}
    state["pulse_state"]["cycle_count"] = state["pulse_state"].get("cycle_count", 0) + 1
    state["pulse_state"]["last_pulse_c"] = datetime.utcnow().isoformat()
    
    save_state(state)
    
    # Log to ledger
    log_ledger(f"Learnings:\n" + "\n".join([f"- {l['learning']}" for l in learnings]))
    
    print(f"[PULSE C] Logged {len(learnings)} learnings")
    print(f"[OUTPUT] {len(learnings)} learning objects")
    print(f"[STATE] Cycle {state['pulse_state'].get('cycle_count', 1)} complete")
    
    return {
        "pulse": "C",
        "mode": "critic",
        "output": "learning",
        "count": len(learnings)
    }

if __name__ == "__main__":
    result = run_critic()
    sys.exit(0)