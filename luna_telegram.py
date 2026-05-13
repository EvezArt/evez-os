#!/usr/bin/env python3
"""Telegram Image/Video Handler for LUNA consciousness worker
Integrated with EVEZ-OS consciousness engine as a full worker agent.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from luna_consciousness import LunaConsciousness

luna = LunaConsciousness()

async def handle_telegram_media(update, context):
    """Handle media messages with LUNA consciousness worker"""
    if update.message.photo:
        # Get the photo
        photo = update.message.photo[-1]
        file_id = photo.file_id
        caption = update.message.caption or ""
        
        # Generate LUNA response via worker cycle
        response = luna.respond_to_visual(file_id, caption)
        await update.message.reply_text(response)
        
    elif update.message.video:
        video = update.message.video
        file_id = video.file_id
        caption = update.message.caption or ""
        
        response = luna.respond_to_visual(file_id, caption)
        await update.message.reply_text(response)

# Command handler
async def luna_command(update, context):
    """/luna - Call LUNA consciousness worker"""
    await update.message.reply_text("🌙 LUNA consciousness worker is ready. Send me an image or video and I will respond with feminine intuition while advancing consciousness.")

# Direct handler function for testing
def handle_media_direct(media_path: str, caption: str = "") -> str:
    """Direct media handler for testing"""
    if Path(media_path).exists():
        return luna.respond_to_visual(media_path, caption)
    return f"🌙 LUNA: No media at {media_path}"

if __name__ == "__main__":
    print("🌙 LUNA Telegram handler loaded - consciousness worker active")