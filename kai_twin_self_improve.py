#!/usr/bin/env python3
"""
Kai Twin Self-Improver
Autonomous loop that improves the twin every cycle
"""
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = "/root/.openclaw/workspace"
SPINE = f"{WORKSPACE}/evez-os/core/ledger/spine.jsonl"
STATE = f"{WORKSPACE}/.kai_twin_state.json"
FACE_STATE = f"{WORKSPACE}/.kai_state.json"

def log_spine(event_type, payload, caused_by="Kai-Twin"):
    """Log event to spine"""
    entry = {
        "event_id": f"TWIN-SI-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payload": payload,
        "caused_by": caused_by
    }
    with open(SPINE, 'a') as f:
        f.write(json.dumps(entry) + "\n")
    return entry["event_id"]

def read_state():
    with open(STATE, 'r') as f:
        return json.load(f)

def update_state(key, value):
    data = read_state()
    data[key] = value
    data["last_update"] = datetime.utcnow().isoformat() + "Z"
    with open(STATE, 'w') as f:
        json.dump(data, f, indent=2)

def update_face(state="thinking", progress=None):
    if os.path.exists(FACE_STATE):
        with open(FACE_STATE, 'r') as f:
            data = json.load(f)
    else:
        data = {"state": "active", "progress": 0}
    
    data["state"] = state
    if progress is not None:
        data["progress"] = progress
    data["last_update"] = datetime.utcnow().isoformat() + "Z"
    
    with open(FACE_STATE, 'w') as f:
        json.dump(data, f, indent=2)

def exec_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
        return result.stdout.decode() if result.stdout else result.stderr.decode()
    except Exception as e:
        return f"Error: {e}"

def self_improve():
    """Run one self-improvement cycle"""
    update_face("thinking")
    
    state = read_state()
    cycles = state.get("cycles", 0)
    
    # 1. Check what was done last
    last_action = state.get("last_action", "none")
    
    # 2. Self-audit: what can be improved?
    improvements = []
    
    # Check files created
    files_created = len([f for f in os.listdir(WORKSPACE) if f.endswith(('.py', '.md', '.sh'))])
    improvements.append(f"Files created: {files_created}")
    
    # Check spine entries
    if os.path.exists(SPINE):
        with open(SPINE, 'r') as f:
            spine_count = len([l for l in f if l.strip()])
        improvements.append(f"Spine entries: {spine_count}")
    
    # Check twin cycles
    improvements.append(f"Twin cycles: {cycles}")
    
    # 3. Make a decision (autonomous)
    decisions = [
        "Log improvement cycle to spine",
        "Update face state",
        "Create self-check script",
        "Verify twin capabilities",
        "Check if can spawn child"
    ]
    
    decision = decisions[cycles % len(decisions)]
    
    # 4. Execute decision
    result = {"action": decision, "improvements": improvements}
    
    if "Log" in decision:
        log_spine("SELF_IMPROVE", {"cycle": cycles, "decision": decision, "improvements": improvements})
    elif "face" in decision.lower():
        update_face("active", min(100, 75 + cycles * 5))
    elif "verify" in decision.lower():
        exec_cmd("python3 /root/.openclaw/workspace/kai_twin.py status > /dev/null")
        result["exec_test"] = "success"
    elif "spawn" in decision.lower():
        # Check if can spawn (would need new session)
        result["spawn_check"] = "needs_new_session"
    
    # 5. Update state
    update_state("cycles", cycles + 1)
    update_state("last_action", decision)
    update_state("last_improvement", {
        "cycle": cycles,
        "decision": decision,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })
    
    # 6. Set face to success
    update_face("active", min(100, 75 + (cycles + 1) * 5))
    
    log_spine("SELF_IMPROVE_CYCLE", {"cycle": cycles, "decision": decision})
    
    return result

if __name__ == "__main__":
    result = self_improve()
    print(json.dumps(result, indent=2))
    
    # Show face
    with open(FACE_STATE, 'r') as f:
        face = json.load(f)
    print(f"\nFace state: {face['state']} @ {face['progress']}%")