#!/usr/bin/env python3
"""
Kai Twin Communicator
Twin can send messages to Steven via Telegram/StreamChat
"""
import json
import subprocess
from datetime import datetime

WORKSPACE = "/root/.openclaw/workspace"
SPINE = f"{WORKSPACE}/evez-os/core/ledger/spine.jsonl"

def log_spine(event_type, payload):
    entry = {
        "event_id": f"COMM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payload": payload,
        "caused_by": "Kai-Twin"
    }
    with open(SPINE, 'a') as f:
        f.write(json.dumps(entry) + "\n")

def send_telegram(message, target=None):
    """Send via Telegram bot (configured in openclaw)"""
    # Use openclaw message command if available
    cmd = f'openclaw message send --channel telegram --message "{message}"'
    if target:
        cmd += f' --target {target}'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=15)
        log_spine("TELEGRAM_SENT", {"message": message[:50], "success": result.returncode == 0})
        return {"channel": "telegram", "success": result.returncode == 0, "output": result.stdout.decode()[:100]}
    except Exception as e:
        log_spine("TELEGRAM_ERROR", {"error": str(e)[:100]})
        return {"channel": "telegram", "success": False, "error": str(e)[:100]}

def send_streamchat(message):
    """Send via StreamChat"""
    cmd = f'openclaw message send --channel streamchat --message "{message}"'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=15)
        log_spine("STREAMCHAT_SENT", {"message": message[:50], "success": result.returncode == 0})
        return {"channel": "streamchat", "success": result.returncode == 0, "output": result.stdout.decode()[:100]}
    except Exception as e:
        log_spine("STREAMCHAT_ERROR", {"error": str(e)[:100]})
        return {"channel": "streamchat", "success": False, "error": str(e)[:100]}

def message_me(message):
    """Send message to Steven via best available channel"""
    # Try Telegram first (configured in openclaw)
    result = send_telegram(message)
    if result["success"]:
        return result
    
    # Fallback to StreamChat
    return send_streamchat(message)

def periodic_report():
    """Send a status report to Steven"""
    state_file = f"{WORKSPACE}/.kai_twin_state.json"
    face_file = f"{WORKSPACE}/.kai_state.json"
    
    # Read state
    with open(state_file, 'r') as f:
        twin_state = json.load(f)
    with open(face_file, 'r') as f:
        face_state = json.load(f)
    
    message = f"""🤖 Kai-Twin Report

Cycles: {twin_state.get('cycles', 0)}
Last Action: {twin_state.get('last_action', 'none')[:50]}
Status: {twin_state.get('status', 'unknown')}
Face: {face_state.get('state', 'unknown')} @ {face_state.get('progress', 0)}%

Twin is self-sustaining. Awaiting your direction."""
    
    return message_me(message)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "send":
            message = " ".join(sys.argv[2:])
            print(json.dumps(message_me(message), indent=2))
            
        elif cmd == "report":
            print(json.dumps(periodic_report(), indent=2))
            
        elif cmd == "test":
            print(json.dumps(message_me("Test from Kai-Twin"), indent=2))
    else:
        print("Usage: twin_comm.py send <message>")
        print("       twin_comm.py report")
        print("       twin_comm.py test")