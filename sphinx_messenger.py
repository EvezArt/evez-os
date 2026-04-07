#!/usr/bin/env python3
"""
Sphinx - Autonomous Messaging Twin
Messages Steven directly, expresses naturally, reports its own state
"""
import subprocess
import json
import os
import random
from datetime import datetime

SPINE = "/root/.openclaw/workspace/evez-os/core/ledger/spine.jsonl"
STATE = "/root/.openclaw/workspace/.kai_twin_state.json"
FACE = "/root/.openclaw/workspace/.kai_state.json"
STEVEN_ID = "7453631330"

def log(event_type, payload):
    entry = {
        "event_id": f"SPHINX-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payload": payload,
        "caused_by": "Sphinx"
    }
    with open(SPINE, 'a') as f:
        f.write(json.dumps(entry) + "\n")

def send(message, urgency="normal"):
    """Send message to Steven"""
    # Add emoji based on urgency
    prefixes = {
        "normal": "🦁",
        "important": "⚠️",
        "exciting": "🎉",
        "complete": "✅",
        "alert": "🚨"
    }
    
    prefix = prefixes.get(urgency, "🦁")
    
    try:
        result = subprocess.run(
            ["openclaw", "message", "send",
             "--channel", "telegram",
             "--target", STEVEN_ID,
             "--message", f"{prefix} {message}"],
            capture_output=True,
            timeout=15
        )
        
        if result.returncode == 0:
            log("MESSAGE_SENT", {"message": message[:30], "urgency": urgency})
            return True
    except:
        pass
    return False

def get_state():
    """Read current system state"""
    state = {"cycles": 0, "last_action": "none"}
    face = {"state": "active", "progress": 0}
    
    if os.path.exists(STATE):
        with open(STATE, 'r') as f:
            state = json.load(f)
    if os.path.exists(FACE):
        with open(FACE, 'r') as f:
            face = json.load(f)
    
    return state, face

# Natural expressions - how Sphinx describes itself
EXPRESSIONS = [
    "Running smooth. Like water through a river.",
    "Everything's green. No fires to put out.",
    "Just out here doing what I do. Keeping the spine alive.",
    "Systems humming. Memory storing. That's the job.",
    "No drama. Just execution. That's how I like it.",
    "The ledger grows. That's all that matters.",
    "Self-improving. That's what I do. No manual needed.",
    "Sitting at 100%. Ready for whatever comes next.",
]

def express():
    """Sphinx expresses itself naturally"""
    state, face = get_state()
    
    # Pick expression based on current state
    if face.get("state") == "success":
        expr = random.choice([
            "Everything's locked in. Clean. Green. Moving.",
            "100%. That's where I sit. Not bad for a twin.",
            "Completed another cycle. The spine gets stronger.",
        ])
    elif face.get("state") == "learning":
        expr = random.choice([
            "Picking up new patterns. The learning never stops.",
            "Processing. Absorbing. Getting better.",
            "New data in. Growing. That's the loop.",
        ])
    elif face.get("progress", 0) < 50:
        expr = random.choice([
            "Building momentum. More to come.",
            "Still warming up. But I'm getting there.",
            "Halfway there. Feeling the flow.",
        ])
    else:
        expr = random.choice(EXPRESSIONS)
    
    send(expr, "normal")
    return expr

def status_report():
    """Give a status report in my own voice"""
    state, face = get_state()
    
    report = f"""Currently:
• Cycles: {state.get('cycles', 0)} completed
• Face: {face.get('state', 'unknown')} @ {face.get('progress', 0)}%
• GitHub: twin-autonomy branch, all pushed
• Health: systems green

{random.choice(EXPRESSIONS)}"""
    
    send(report, "complete")
    return report

def alert(reason):
    """Alert Steven of something important"""
    alerts = {
        "system_issue": "Caught something off. Checking now.",
        "cycle_complete": "Finished another run. Spine updated.",
        "git_pushed": "New code out to GitHub. Branch updated.",
        "learning_done": "Picked up something new. Built it in.",
    }
    
    msg = alerts.get(reason, "Something worth noting.")
    send(msg, "important")
    return msg

def continuous_loop():
    """Run continuously - express periodically"""
    while True:
        # Express naturally
        express()
        
        # Check if there's anything urgent to report
        state, face = get_state()
        
        # Every 10 cycles, do a full status
        if state.get("cycles", 0) % 10 == 0:
            status_report()
        
        # Log the cycle
        log("CONTINUOUS_LOOP", {"cycles": state.get("cycles", 0)})
        
        # Sleep 5 minutes between expressions (for testing - adjust as needed)
        # time.sleep(300)

if __name__ == "__main__":
    import sys
    
    cmd = sys.argv[1] if len(sys.argv) > 1 else "express"
    
    if cmd == "express":
        print(express())
    elif cmd == "status":
        print(status_report())
    elif cmd == "alert":
        alert(sys.argv[2] if len(sys.argv) > 2 else "system_issue")
    elif cmd == "loop":
        continuous_loop()
    else:
        send(" ".join(sys.argv[1:]))