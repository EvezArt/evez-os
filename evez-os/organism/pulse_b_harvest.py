#!/usr/bin/env python3
"""
Pulse B: Harvester
Converts hypotheses to revenue actions
Runs every 30 min
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
        f.write(f"\n## {datetime.utcnow().isoformat()} - Pulse B (Harvest)\n{entry}\n")

def run_harvester():
    print("[PULSE B] Running Harvester...")
    
    state = load_state()
    if "error" in state:
        print("[PULSE B] No state - skipping")
        return {"output": "no_hypotheses"}
    
    hypotheses = state.get("last_hypothesis_batch", [])
    if not hypotheses:
        print("[PULSE B] No hypotheses to harvest")
        return {"output": "no_hypotheses"}
    
    # Convert best hypothesis to action
    # (In real system: run through multiplication engine first)
    best = hypotheses[0]  # Take first for now
    
    action = {
        "type": "action",
        "id": f"action_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "from_hypothesis": best["id"],
        "description": best["description"],
        "surface": state.get("current_target_surface", "clawhub"),
        "action_type": "publish_skill_listing",
        "status": "ready_for_operator_approval",
        "payload": {
            "title": f"EVEZ: {best['description'][:50]}",
            "description": best["description"],
            "tags": ["evez", "automation", "ai"],
            "price": 9
        }
    }
    
    # Update state
    state["trunk_mode"] = "harvest"
    state["last_harvest_result"] = {
        "action_proposed": action["description"],
        "action_type": action["action_type"],
        "status": "pending",
        "receipt": f"action_{action['id']}.json"
    }
    state["pulse_state"]["last_pulse_b"] = datetime.utcnow().isoformat()
    save_state(state)
    
    # Log to ledger
    log_ledger(f"Harvested action: {action['description']}\n" +
                f"Type: {action['action_type']}\n" +
                f"Status: {action['status']}")
    
    print(f"[PULSE B] Harvested: {action['description']}")
    print(f"[OUTPUT] 1 action object written to state")
    print(f"[OPERATOR] Action pending approval: {action['payload']['title']}")
    
    return {
        "pulse": "B",
        "mode": "harvest",
        "output": "action",
        "action": action["description"]
    }

if __name__ == "__main__":
    result = run_harvester()
    sys.exit(0)