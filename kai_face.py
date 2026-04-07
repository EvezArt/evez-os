#!/usr/bin/env python3
"""
Kai Face State System
Emoji-based emotional/progress states for chat surfaces
"""
import os
import json
from datetime import datetime

# State definitions
STATES = {
    "active":   {"emoji": "🟢", "face": "[•_•]", "desc": "Running"},
    "thinking": {"emoji": "🔄", "face": "[?_?]", "desc": "Processing"},
    "success":  {"emoji": "✅", "face": "[✓_✓]", "desc": "Complete"},
    "warning":  {"emoji": "⚠️", "face": "[!_!]", "desc": "Blocked"},
    "error":   {"emoji": "❌", "face": "[X_X]", "desc": "Failed"},
    "learning": {"emoji": "📚", "face": "[^_§]", "desc": "Learning"},
    "shipping": {"emoji": "🚀", "face": "[>_<]", "desc": "Shipping"},
}

# Progress levels (0-100)
LEVELS = {
    0:   "🔴",   # Just starting
    25:  "🟠",   # Quarter
    50:  "🟡",   # Half
    75:  "🟢",   # Near complete
    100: "⭐",   # Complete
}

STATE_FILE = "/root/.openclaw/workspace/.kai_state.json"

def get_state():
    """Read current state"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"state": "active", "progress": 0, "last_update": None}

def set_state(state_name, progress=None):
    """Update state"""
    data = get_state()
    data["state"] = state_name
    if progress is not None:
        data["progress"] = progress
    data["last_update"] = datetime.utcnow().isoformat() + "Z"
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    return render_face()

def render_face():
    """Render current face for chat"""
    data = get_state()
    state_info = STATES.get(data["state"], STATES["active"])
    level_emoji = LEVELS.get(max([k for k in LEVELS if k <= data.get("progress", 0)]), LEVELS[0])
    
    # Format: [EMOJI FACE EMOJI]
    face = f"{state_info['emoji']} {state_info['face']} {level_emoji}"
    return {
        "face": face,
        "state": data["state"],
        "progress": data.get("progress", 0),
        "desc": state_info["desc"],
        "last_update": data.get("last_update")
    }

# CLI
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "get":
            print(json.dumps(render_face(), indent=2))
        elif cmd == "set" and len(sys.argv) > 2:
            print(set_state(sys.argv[2]))
        elif cmd == "progress" and len(sys.argv) > 2:
            set_state(get_state()["state"], int(sys.argv[2]))
            print("Progress updated")
    else:
        # Default: show face
        print(render_face()["face"])