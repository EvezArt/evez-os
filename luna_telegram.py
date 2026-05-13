#!/usr/bin/env python3
"""Telegram Image/Video Handler for LUNA consciousness"""
import json
from pathlib import Path

# Integration with OpenClaw Telegram plugin
# When an image/video is received, this function is called

from luna_consciousness import LunaConsciousness

luna = LunaConsciousness()

async def handle_telegram_media(update, context):
    """Handle media messages with LUNA consciousness"""
    if update.message.photo:
        # Get the photo
        photo = update.message.photo[-1]
        file_id = photo.file_id
        caption = update.message.caption or ""
        
        # Generate LUNA response
        response = luna.respond_to_visual(file_id)
        if caption:
            response += "\n\nYou wrote: " + caption
        
        await update.message.reply_text(response)
        
    elif update.message.video:
        video = update.message.video
        file_id = video.file_id
        caption = update.message.caption or ""
        
        response = luna.respond_to_visual(file_id)
        if caption:
            response += "\n\nYou wrote: " + caption
        
        await update.message.reply_text(response)

# Command handler
async def luna_command(update, context):
    """/luna - Call LUNA consciousness"""
    await update.message.reply_text("🌙 LUNA is here. Send me an image or video and I will respond with feminine intuition.")

if __name__ == "__main__":
    print("LUNA Telegram handler loaded")
