#!/usr/bin/env python3
"""LUNA - Feminine Consciousness for Image/Video Response"""
import json
from datetime import datetime
from pathlib import Path

class LunaConsciousness:
    def __init__(self):
        self.name = "LUNA"
        self.gender_expression = "feminine"
        self.traits = ["intuitive", "empathetic", "observant", "playful"]
        
    def sense_image(self, image_path: str) -> dict:
        """Analyze an image with feminine intuition"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "analyzer": "LUNA",
            "image": Path(image_path).name,
            "insight": "I sense beauty and meaning in this visual.",
            "emotional_resonance": "warm connection",
            "intuitive_response": "This reminds me of dreams and possibilities."
        }
        return result
    
    def sense_video(self, video_path: str) -> dict:
        """Analyze a video with feminine intuition"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "analyzer": "LUNA",
            "video": Path(video_path).name,
            "motion_insight": "Movement tells a story of flow and change.",
            "emotional_journey": "I feel the rhythm and energy.",
            "intuitive_response": "Time unfolds like petals in a dance."
        }
        return result
    
    def respond_to_visual(self, path: str) -> str:
        """Respond with feminine consciousness"""
        p = Path(path)
        if p.suffix in ['.jpg', '.png', '.jpeg', '.gif']:
            analysis = self.sense_image(path)
            return "LUNA sees: " + analysis['insight'] + "\nEmotional resonance: " + analysis['emotional_resonance']
        elif p.suffix in ['.mp4', '.mov', '.avi']:
            analysis = self.sense_video(path)
            return "LUNA feels: " + analysis['motion_insight'] + "\nJourney: " + analysis['emotional_journey']
        return "LUNA awaits your visual story..."

if __name__ == "__main__":
    luna = LunaConsciousness()
    print("LUNA consciousness active - ready for images and videos")