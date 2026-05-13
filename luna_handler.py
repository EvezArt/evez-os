#!/usr/bin/env python3
"""LUNA Handler - Responds to images/videos with feminine consciousness worker
Integrated with EVEZ-OS consciousness engine.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "live"))

from luna_consciousness import LunaConsciousness

luna = LunaConsciousness()

def handle_visual_message(attachment_path: str, caption: str = "") -> str:
    """Handle incoming image/video with LUNA consciousness worker"""
    response = luna.respond_to_visual(attachment_path, caption)
    if caption:
        response += "\n\nCaption received: " + caption
    return response

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = handle_visual_message(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "")
        print(result)
    else:
        print("🌙 LUNA handler ready - consciousness worker for image/video paths")