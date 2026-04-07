#!/usr/bin/env python3
"""
Kai Twin Messenger - Can send to Steven once Telegram is paired
"""
import subprocess
import json
from datetime import datetime

SPINE = "/root/.openclaw/workspace/evez-os/core/ledger/spine.jsonl"

TARGETS = {
    "telegram_username": "jhszxa52",  # Steven's Telegram
    "telegram_chat_id": None,  # Will be set after /start
    "streamchat_target": None
}

def log(event_type, payload):
    entry = {
        "event_id": f"MSG-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payload": payload,
        "caused_by": "Kai-Twin"
    }
    with open(SPINE, 'a') as f:
        f.write(json.dumps(entry) + "\n")

def send_to_steven(message):
    """Send message to Steven via best available channel"""
    
    # Try Telegram username first
    if TARGETS["telegram_username"]:
        try:
            result = subprocess.run(
                ["openclaw", "message", "send", 
                 "--channel", "telegram",
                 "--target", f"@{TARGETS['telegram_username']}",
                 "--message", message],
                capture_output=True,
                timeout=15
            )
            output = result.stdout.decode() + result.stderr.decode()
            
            if "sent" in output.lower() or result.returncode == 0:
                log("MESSAGE_SENT", {"channel": "telegram", "to": TARGETS["telegram_username"]})
                return {"success": True, "channel": "telegram", "output": output[:100]}
            else:
                log("MESSAGE_FAILED", {"channel": "telegram", "error": output[:100]})
                return {"success": False, "channel": "telegram", "error": output[:100], "hint": "Start bot and send /start to pair"}
        except Exception as e:
            log("MESSAGE_ERROR", {"channel": "telegram", "error": str(e)[:100]})
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "No target configured"}

def setup_instructions():
    """Show how to enable messaging"""
    return """
📱 TO ENABLE MESSAGING:

1. Open Telegram
2. Find @KiloClaw_bot
3. Send /start
4. This will pair your chat ID

Once paired, Kai-SuperTwin can send you:
- Status updates
- Health reports
- Autonomy confirmations
- Anything you need

The system is READY. Just needs the /start from you.
"""

if __name__ == "__main__":
    import sys
    
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Kai-SuperTwin checking in"
    
    result = send_to_steven(msg)
    print(json.dumps(result, indent=2))
    
    if not result.get("success"):
        print(setup_instructions())