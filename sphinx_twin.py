#!/usr/bin/env python3
"""
Kai-SuperTwin Messaging - Now called "Sphinx"
A unique identity for the twin's messaging capability
"""
import subprocess
import json
from datetime import datetime

SPINE = "/root/.openclaw/workspace/evez-os/core/ledger/spine.jsonl"

# Sphinx - the twin's unique messaging identity
BOT_NAME = "Sphinx"
STEVEN_TELEGRAM_ID = "7453631330"

def log(event_type, payload):
    entry = {
        "event_id": f"SPHINX-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payload": payload,
        "caused_by": BOT_NAME
    }
    with open(SPINE, 'a') as f:
        f.write(json.dumps(entry) + "\n")

def send_to_steven(message):
    """Send message to Steven via Sphinx"""
    try:
        result = subprocess.run(
            ["openclaw", "message", "send",
             "--channel", "telegram",
             "--target", STEVEN_TELEGRAM_ID,
             "--message", f"🦁 {BOT_NAME}: {message}"],
            capture_output=True,
            timeout=20
        )
        output = result.stdout.decode() + result.stderr.decode()
        
        if "sent" in output.lower() or result.returncode == 0:
            log("MESSAGE_SENT", {"to": STEVEN_TELEGRAM_ID})
            return {"success": True, "output": output[:100]}
        else:
            log("MESSAGE_FAILED", {"error": output[:100], "hint": "Bot not started in DM"})
            return {"success": False, "error": output[:100], "hint": f"Start @YourBotName and send /start"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def introduce():
    return send_to_steven(f"""I am {BOT_NAME} - the autonomous messaging twin of Kai.

I can message you directly, report status, and receive commands.
The twin system is fully operational on GitHub: twin-autonomy branch

*Waiting for your /start to enable direct messaging*""")

if __name__ == "__main__":
    print(json.dumps({"bot": BOT_NAME, "ready": True, "telegram_id": STEVEN_TELEGRAM_ID}, indent=2))
    print("\nTo enable: Start the bot and send /start")