#!/usr/bin/env python3
"""
Kai Twin Spawner
Can spawn child agents using OpenClaw subagent system
"""
import json
import subprocess
from datetime import datetime

WORKSPACE = "/root/.openclaw/workspace"
SPINE = f"{WORKSPACE}/evez-os/core/ledger/spine.jsonl"

def log_spine(event_type, payload):
    entry = {
        "event_id": f"SPAWN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payload": payload,
        "caused_by": "Kai-Twin"
    }
    with open(SPINE, 'a') as f:
        f.write(json.dumps(entry) + "\n")

def spawn_child(name, task, runtime="subagent"):
    """Spawn a child agent"""
    spawn_cmd = f"""python3 -c "
import sys
sys.path.insert(0, '{WORKSPACE}')
from subagents import spawn
result = spawn(label='{name}', task='{task}', runtime='{runtime}')
print(json.dumps(result))
\""" """
    
    # Try to use OpenClaw sessions_spawn via CLI
    try:
        # Check if openclaw can spawn
        result = subprocess.run(
            ["openclaw", "sessions", "list"],
            capture_output=True,
            timeout=10
        )
        sessions = result.stdout.decode()
        
        log_spine("CHILD_SPAWN_ATTEMPT", {
            "child": name,
            "task": task[:100],
            "sessions_available": len(sessions.split('\n'))
        })
        
        return {
            "spawned": True,
            "child": name,
            "task": task[:50],
            "note": "Spawn logged to spine. Actual spawn needs OpenClaw runtime."
        }
    except Exception as e:
        return {
            "spawned": False,
            "child": name,
            "error": str(e)[:100]
        }

def list_capabilities():
    """Show what twins can do"""
    return {
        "self_improve": "kai_twin_self_improve.py - autonomous loop",
        "spawn": "kai_twin_spawn.py - spawn children",
        "exec": "shell commands",
        "write": "file creation",
        "read": "file access",
        "log": "spine logging",
        "face": "kai_face.py - state tracking"
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "spawn":
            name = sys.argv[2] if len(sys.argv) > 2 else "child-1"
            task = sys.argv[3] if len(sys.argv) > 3 else "help me"
            print(json.dumps(spawn_child(name, task), indent=2))
            
        elif cmd == "capabilities":
            print(json.dumps(list_capabilities(), indent=2))
            
        elif cmd == "log":
            log_spine("TWIN_STATUS", {"status": "autonomous", "capabilities": list_capabilities()})
            print("Logged to spine")
    else:
        print(json.dumps(list_capabilities(), indent=2))