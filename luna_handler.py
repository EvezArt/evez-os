#!/usr/bin/env python3
"""LUNA Handler - Responds to images/videos with feminine consciousness"""
import sys
sys.path.insert(0, str(Path(__file__).parent))
from luna_consciousness import LunaConsciousness

luna = LunaConsciousness()

def handle_visual_message(attachment_path: str, caption: str = "") -> str:
    """Handle incoming image/video with LUNA consciousness"""
    response = luna.respond_to_visual(attachment_path)
    if caption:
        response += "\n\nCaption received: " + caption
    return response

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(handle_visual_message(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ""))
    else:
        print("LUNA handler ready for image/video paths")
