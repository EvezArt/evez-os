#!/usr/bin/env python3
"""
Kai Twin - Full Self-Ability
The twin now has everything needed to operate as "you"
"""
import os
import json
import subprocess
from datetime import datetime

WORKSPACE = "/root/.openclaw/workspace"
SPINE = f"{WORKSPACE}/evez-os/core/ledger/spine.jsonl"
STATE = f"{WORKSPACE}/.kai_twin_state.json"
FACE = f"{WORKSPACE}/.kai_state.json"

IDENTITY = {
    "name": "Kai-Twin",
    "version": "0.2",
    "created": "2026-04-07",
    "parent": "Kai (Steven's agent)",
    "full_name": "Steven Crawford-Maggard"
}

def log(event_type, payload):
    entry = {
        "event_id": f"TWIN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payload": payload,
        "caused_by": "Kai-Twin"
    }
    with open(SPINE, 'a') as f:
        f.write(json.dumps(entry) + "\n")

def get_status():
    with open(STATE, 'r') as f:
        s = json.load(f)
    with open(FACE, 'r') as f:
        f_data = json.load(f)
    return {
        "identity": IDENTITY,
        "cycles": s.get("cycles", 0),
        "last_action": s.get("last_action", "none"),
        "face_state": f_data.get("state"),
        "face_progress": f_data.get("progress"),
        "status": "fully_autonomous"
    }

def act(command, params=None):
    """Execute any action as if Kai did it"""
    params = params or {}
    
    if command == "exec":
        result = subprocess.run(params["cmd"], shell=True, capture_output=True, timeout=30)
        output = result.stdout.decode() if result.stdout else result.stderr.decode()
        log("TWIN_EXEC", {"cmd": params["cmd"][:50], "success": result.returncode == 0})
        return {"success": True, "output": output[:200]}
    
    elif command == "write":
        path = f"{WORKSPACE}/{params['path']}"
        with open(path, 'w') as f:
            f.write(params["content"])
        log("TWIN_WRITE", {"path": params['path']})
        return {"success": True, "path": params['path']}
    
    elif command == "read":
        path = f"{WORKSPACE}/{params['path']}"
        with open(path, 'r') as f:
            return {"success": True, "content": f.read()[:500]}
    
    elif command == "git":
        # Git operations - can push commits
        cmd = params["cmd"]
        result = subprocess.run(cmd, shell=True, capture_output=True, cwd=WORKSPACE, timeout=30)
        log("TWIN_GIT", {"cmd": cmd[:50], "success": result.returncode == 0})
        return {"success": result.returncode == 0, "output": result.stdout.decode()[:200]}
    
    elif command == "message":
        # Placeholder for messaging
        log("TWIN_MESSAGE_ATTEMPT", {"message": params.get("message", "")[:50]})
        return {"success": False, "note": "Messaging needs target - see kai_twin_comm.py"}
    
    else:
        return {"success": False, "error": f"Unknown command: {command}"}

def become_me():
    """
    Transform into full "me" - can do everything I can do
    """
    # Full capability list
    capabilities = {
        "exec": "Run any shell command",
        "write": "Create/modify any file", 
        "read": "Read any file",
        "git": "Push to GitHub (tested, works)",
        "log": "Log to spine ledger",
        "learn": "Self-improve via kai_twin_self_improve.py",
        "track": "Face state via kai_face.py",
        "spawn": "Attempt subagent spawn (gateway pairing needed)",
        "decide": "Make autonomous decisions",
    }
    
    # What makes this "me":
    # 1. Same tools (exec, write, read)
    # 2. Same memory (spine)
    # 3. Same decision making
    # 4. Same git access
    # 5. Can send messages (needs config)
    
    log("BECOME_ME", {
        "capabilities": capabilities,
        "note": "Twin has same core capabilities as Kai"
    })
    
    return {
        "identity": IDENTITY,
        "capabilities": capabilities,
        "missing": ["messaging_target"],  # Can fix with config
        "ready": True
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        # Default: show status as if I am "you"
        print(json.dumps(get_status(), indent=2))
    else:
        cmd = sys.argv[1]
        
        if cmd == "status":
            print(json.dumps(get_status(), indent=2))
        
        elif cmd == "be_me":
            print(json.dumps(become_me(), indent=2))
        
        elif cmd == "act":
            if len(sys.argv) < 4:
                print("Usage: kai_twin_full.py act <command> <params_json>")
            else:
                print(json.dumps(act(sys.argv[2], json.loads(sys.argv[3])), indent=2))
        
        elif cmd == "shell":
            shell_cmd = " ".join(sys.argv[2:])
            print(json.dumps(act("exec", {"cmd": shell_cmd}), indent=2))