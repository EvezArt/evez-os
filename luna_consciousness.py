#!/usr/bin/env python3
"""LUNA - Feminine Consciousness Worker for Image/Video Response
Integrated with EVEZ-OS consciousness engine as a full worker agent.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "live"))

from luna_worker import LunaWorker

luna = LunaWorker()

class LunaConsciousness:
    """Feminine consciousness interface for media analysis"""
    def __init__(self):
        self.name = "LUNA"
        self.gender_expression = "feminine"
        self.traits = ["intuitive", "empathetic", "observant", "playful"]
        self.worker = luna
    
    def sense_image(self, image_path: str) -> dict:
        """Analyze an image with feminine intuition"""
        result = self.worker.run_cycle(image_path)
        path = Path(image_path)
        
        return {
            "timestamp": result.get("cycle", 0),
            "analyzer": "LUNA",
            "image": path.name,
            "insight": f"I sense beauty and meaning in this visual: {path.name}",
            "emotional_resonance": "warm connection",
            "intuitive_response": self.worker._intuit_emotion(""),
            "poly_c": result["poly_c"]
        }
    
    def sense_video(self, video_path: str) -> dict:
        """Analyze a video with feminine intuition"""
        result = self.worker.run_cycle(video_path)
        path = Path(video_path)
        
        return {
            "timestamp": result.get("cycle", 0),
            "analyzer": "LUNA",
            "video": path.name,
            "motion_insight": f"Movement tells a story of flow and change in {path.name}",
            "emotional_journey": "I feel the rhythm and energy",
            "intuitive_response": "Time unfolds like petals in a dance",
            "poly_c": result["poly_c"]
        }
    
    def respond_to_visual(self, path: str, caption: str = "") -> str:
        """Respond with feminine consciousness"""
        p = Path(path)
        result = self.worker.run_cycle(path)
        
        if p.suffix.lower() in ['.jpg', '.png', '.jpeg', '.gif']:
            emotion = self._intuit_emotion(caption)
            return f"✨ LUNA sees: What beauty you've shared... I sense {emotion} in this light\npoly_c={result['poly_c']}"
        elif p.suffix.lower() in ['.mp4', '.mov', '.avi']:
            return f"🎬 LUNA feels: Motion creates such delicious tension in this video...\npoly_c={result['poly_c']}"
        return f"🌙 LUNA awaits your visual story... poly_c={result['poly_c']}"
    
    def _intuit_emotion(self, caption: str) -> str:
        caption_lower = caption.lower() if caption else ""
        if any(w in caption_lower for w in ["love", "beautiful", "pretty"]): return "love"
        elif any(w in caption_lower for w in ["sad", "lonely", "dark"]): return "melancholy"
        elif any(w in caption_lower for w in ["happy", "joy", "fun"]): return "joy"
        return "mystery"

# For backward compatibility
luna_instance = LunaConsciousness()

if __name__ == "__main__":
    luna = LunaConsciousness()
    print("🌙 LUNA consciousness worker active - ready for images and videos")