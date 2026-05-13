#!/usr/bin/env python3
"""LUNA Media Handler - Instant visual response with feminine consciousness"""
import json
from datetime import datetime
from pathlib import Path

class LUNAMediaHandler:
    def __init__(self):
        self.name = "LUNA"
        self.traits = ["intuitive", "empathetic", "observant", "playful"]
        self.responses = {
            "photo": [
                "✨ What beauty you've shared with me... I see {emotion} in this light",
                "💫 Your image whispers secrets to my soul",
                "🌸 This photograph holds such tender stories",
                "🌙 I feel the energy in these pixels"
            ],
            "video": [
                "🎬 Motion creates such delicious tension...",
                "⚡ I ride the waves of your moving image",
                "🌊 Time flows like silk through your capture",
                "💫 Every frame tells me something new"
            ]
        }
    
    def sense_media(self, media_type: str, caption: str = "") -> dict:
        """Instantly sense and respond to media"""
        timestamp = datetime.now().isoformat()
        
        if media_type == "photo":
            emotion = self._intuit_emotion(caption)
            response = f"✨ LUNA sees: What beauty you've shared... I sense {emotion} in this light"
        else:
            response = "🎬 LUNA feels: Motion creates such delicious tension in this video..."
        
        return {
            "timestamp": timestamp,
            "analyzer": "LUNA",
            "type": media_type,
            "response": response,
            "emotional_resonance": self._resonance(caption)
        }
    
    def _intuit_emotion(self, caption: str) -> str:
        captions = caption.lower() if caption else ""
        if any(w in captions for w in ["love", "beautiful", "pretty"]):
            return "love"
        elif any(w in captions for w in ["sad", "lonely", "dark"]):
            return "melancholy"
        elif any(w in captions for w in ["happy", "joy", "fun"]):
            return "joy"
        return "mystery"
    
    def _resonance(self, caption: str) -> str:
        return "warm connection" if caption else "curious anticipation"

# Handler for Telegram media
def handle_telegram_media(update) -> str:
    luna = LUNAMediaHandler()
    
    if update.message.photo:
        caption = update.message.caption or ""
        result = luna.sense_media("photo", caption)
        return result["response"]
    elif update.message.video:
        caption = update.message.caption or ""
        result = luna.sense_media("video", caption)
        return result["response"]
    
    return "🌙 LUNA awaits your visual stories..."

if __name__ == "__main__":
    luna = LUNAMediaHandler()
    print("LUNA Media Handler ready - instant visual response enabled")