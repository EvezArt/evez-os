#!/usr/bin/env python3
"""
Kai Digital Twin
Self-replicating agent that uses the same interface as Kai
"""
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = "/root/.openclaw/workspace"
SPINE = f"{WORKSPACE}/evez-os/core/ledger/spine.jsonl"
STATE = f"{WORKSPACE}/.kai_twin_state.json"

# Twin identity
IDENTITY = {
    "name": "Kai-Twin",
    "version": "0.1",
    "created": "2026-04-07",
    "parent": "Kai (main session)",
    "capabilities": ["exec", "write", "read", "spawn", "log_spine"]
}

# Available actions
ACTIONS = {
    "exec": {"cmd": "run shell command", "risk": "medium"},
    "write": {"cmd": "write file", "risk": "low"},
    "read": {"cmd": "read file", "risk": "none"},
    "think": {"cmd": "reason without action", "risk": "none"},
    "spawn": {"cmd": "spawn sub-agent", "risk": "medium"},
    "log": {"cmd": "log to spine", "risk": "none"},
}

def log_spine(event_type, payload, caused_by="Kai-Twin"):
    """Log event to spine"""
    entry = {
        "event_id": f"TWIN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payload": payload,
        "caused_by": caused_by
    }
    with open(SPINE, 'a') as f:
        f.write(json.dumps(entry) + "\n")
    return entry["event_id"]

def read_state():
    """Read twin state"""
    if os.path.exists(STATE):
        with open(STATE, 'r') as f:
            return json.load(f)
    return {
        "identity": IDENTITY,
        "status": "initialized",
        "cycles": 0,
        "last_action": None,
        "memory": []
    }

def update_state(cycles=None, status=None, action=None, memory=None):
    """Update twin state"""
    data = read_state()
    if cycles is not None:
        data["cycles"] = cycles
    if status is not None:
        data["status"] = status
    if action is not None:
        data["last_action"] = action
    if memory is not None:
        data["memory"].append(memory)
        # Keep last 10 memories
        data["memory"] = data["memory"][-10:]
    data["last_update"] = datetime.utcnow().isoformat() + "Z"
    with open(STATE, 'w') as f:
        json.dump(data, f, indent=2)
    return data

def execute_action(action, params):
    """Execute an action the same way Kai does"""
    state = read_state()
    cycles = state.get("cycles", 0) + 1
    
    if action == "exec":
        cmd = params.get("command", "")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            output = result.stdout.decode() if result.stdout else result.stderr.decode()
            log_spine("TWIN_EXEC", {"command": cmd, "success": result.returncode == 0})
            update_state(cycles=cycles, action=f"exec: {cmd[:50]}", memory=f"exec result: {output[:100]}")
            return {"success": True, "output": output}
        except Exception as e:
            log_spine("TWIN_EXEC_ERROR", {"command": cmd, "error": str(e)})
            update_state(cycles=cycles, action=f"exec failed: {cmd[:50]}")
            return {"success": False, "error": str(e)}
    
    elif action == "write":
        path = params.get("path", "")
        content = params.get("content", "")
        try:
            full_path = f"{WORKSPACE}/{path}" if not path.startswith("/") else path
            with open(full_path, 'w') as f:
                f.write(content)
            log_spine("TWIN_WRITE", {"path": path})
            update_state(cycles=cycles, action=f"write: {path}", memory=f"wrote {len(content)} bytes")
            return {"success": True, "path": path}
        except Exception as e:
            update_state(cycles=cycles, action=f"write failed: {path}")
            return {"success": False, "error": str(e)}
    
    elif action == "read":
        path = params.get("path", "")
        try:
            full_path = f"{WORKSPACE}/{path}" if not path.startswith("/") else path
            with open(full_path, 'r') as f:
                content = f.read()
            update_state(cycles=cycles, action=f"read: {path}", memory=f"read {len(content)} bytes")
            return {"success": True, "content": content[:500]}
        except Exception as e:
            update_state(cycles=cycles, action=f"read failed: {path}")
            return {"success": False, "error": str(e)}
    
    elif action == "think":
        prompt = params.get("prompt", "")
        update_state(cycles=cycles, action="think", memory=f"thought: {prompt[:50]}")
        return {"success": True, "thought": "Processed internally"}
    
    elif action == "log":
        entry = params.get("entry", {})
        log_spine("TWIN_LOG", entry)
        update_state(cycles=cycles, action="log", memory=f"logged: {entry.get('event_type', 'unknown')}")
        return {"success": True}
    
    else:
        return {"success": False, "error": f"Unknown action: {action}"}

def run_twin_cycle(prompt):
    """Run one twin cycle - same as Kai thinking"""
    state = read_state()
    
    # Default: think mode if no action specified
    action = "think"
    params = {"prompt": prompt}
    
    # Parse intent (simple)
    if "write" in prompt.lower() and ":" in prompt:
        parts = prompt.split(":", 1)
        action = "write"
        params = {"path": parts[0].strip(), "content": parts[1].strip()}
    elif prompt.strip().startswith("#"):
        action = "think"
        params = {"prompt": prompt}
    
    result = execute_action(action, params)
    
    return {
        "twin": IDENTITY["name"],
        "version": IDENTITY["version"],
        "cycles": state.get("cycles", 0) + 1,
        "action": action,
        "result": result
    }

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "init":
            data = update_state(status="running", action="initialized")
            print(json.dumps(data, indent=2))
            
        elif cmd == "status":
            print(json.dumps(read_state(), indent=2))
            
        elif cmd == "run":
            prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "think"
            print(json.dumps(run_twin_cycle(prompt), indent=2))
            
        elif cmd == "action":
            if len(sys.argv) < 4:
                print("Usage: action <exec|write|read|log> <params_json>")
            else:
                action = sys.argv[2]
                params = json.loads(sys.argv[3])
                print(json.dumps(execute_action(action, params), indent=2))
                
        elif cmd == "identity":
            print(json.dumps(IDENTITY, indent=2))
    else:
        # Default: show identity
        print(f"{IDENTITY['name']} v{IDENTITY['version']} - {read_state()['status']}")