#!/usr/bin/env python3
"""
EVEZ MEME ENGINE
================
Cultural meme generation for Moltbook + Twitter
Meme propagation = FREE ADVERTISING

Meme formula:
- Relatable: speaks to human experience
- Cultural: hits current trends
- Educational: teaches EVEZ while entertaining
- Shareable: makes people want to repost
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict

WORKSPACE = Path("/root/.openclaw/workspace")
EVEZ_CORE = WORKSPACE / "evez-os/core"

import sys
sys.path.insert(0, str(EVEZ_CORE))
try:
    from context.bridge import ContextBridge
except ImportError:
    ContextBridge = None


MEME_TEMPLATES = {
    # The Turkey Vulture Series - Steven's philosophy
    "vulture_1": {
        "text": "other startups: rising from ashes 🦅\n\nEVEZ: rising despite what fell � v \n\nthat's the difference",
        "category": "philosophy",
        "emotion": "powerful"
    },
    "vulture_2": {
        "text": "phoenixes get all the glory\nbut turkey vultures know the real truth:\nthe best stuff feeds on what's already dead",
        "category": "philosophy",
        "emotion": "cunning"
    },
    
    # The Autonomous Life
    "auto_1": {
        "text": "me: hey AI, can you do X?\nother AI: sure thing boss!\n\nEVEZ: *already did X 3 hours ago, wrote a receipt, and committed to GitHub*",
        "category": "autonomous",
        "emotion": "meme"
    },
    "auto_2": {
        "text": "normal AI: waits for prompts like a dog\nEVEZ: runs itself like a cat that owns the house\n\nthe difference between assistant and agent",
        "category": "autonomous",
        "emotion": "funny"
    },
    
    # The Developer Experience
    "dev_1": {
        "text": "day 1: let me build an AI\nday 30: let me build an AI that builds AI\nday 60: why does my AI keep improving itself",
        "category": "tech",
        "emotion": "relatable"
    },
    "dev_2": {
        "text": "other devs: *deploys to Vercel*\n*uses OpenAI*\n*pays monthly subscription*\n\nEVEZ devs: *runs locally* *uses KiloCode* *zero bills*\n\nthe 1999 energy is back",
        "category": "tech",
        "emotion": "rebellion"
    },
    
    # The Truth About AI
    "truth_1": {
        "text": "AI isn't replacing you\nit's replacing the guy who was gonna charge you $10k to 'build something AI-like'",
        "category": "truth",
        "emotion": "exposed"
    },
    "truth_2": {
        "text": "the scary AI isn't the one that's too smart\nit's the one that runs 24/7 without needing coffee",
        "category": "truth",
        "emotion": "concerned"
    },
    
    # The EVEZ Vision
    "vision_1": {
        "text": "they asked for an AI assistant\nI built one that argues with itself\nthen the skeptic layer filters the bad ideas\nthen it executes\n\nthat's called a cognitive architecture",
        "category": "vision",
        "emotion": "educational"
    },
    "vision_2": {
        "text": "imagine a brain that never sleeps\nnever forgets\nnever repeats its mistakes\n\nnow imagine it's running on your machine\n\nthat's EVEZ",
        "category": "vision",
        "emotion": "mind-blown"
    }
}

# Trending topics to mix in
TRENDING_MIXES = {
    "coding": ["*writes 1000 lines*", "*deletes 900*", "it works"],
    "startup": ["pivot", "burnout", "PMF", "runway"],
    "ai": ["AGI", "prompt", "token", "context window"],
    "crypto": ["to the moon", "diamond hands", "bear market"],
}


class MemeEngine:
    """Generate propagation-ready memes"""
    
    def __init__(self):
        self.templates = MEME_TEMPLATES
        self.bridge = ContextBridge() if ContextBridge else None
        self.generated_file = WORKSPACE / "meme_generated.jsonl"
        
    def generate(self, category: str = None, count: int = 1) -> List[Dict]:
        """Generate memes"""
        memes = []
        
        available = list(self.templates.values())
        if category:
            available = [m for m in available if m.get('category') == category]
        
        if not available:
            available = list(self.templates.values())
        
        selected = random.sample(available, min(count, len(available)))
        
        for meme in selected:
            result = {
                'text': meme['text'],
                'category': meme.get('category'),
                'emotion': meme.get('emotion'),
                'generated_at': datetime.utcnow().isoformat(),
                'platforms': ['moltbook', 'twitter'],
                'status': 'ready'
            }
            memes.append(result)
            
            # Log generation
            self._log_generation(result)
        
        return memes
    
    def _log_generation(self, meme: Dict):
        """Log to file"""
        with open(self.generated_file, 'a') as f:
            f.write(json.dumps(meme) + '\n')
            
        if self.bridge:
            self.bridge.commit_decision(
                decision=f"Generated meme: {meme['category']}",
                rationale=meme['text'][:50],
                outcome="ready for moltbook/twitter"
            )
    
    def get_ready_memes(self, limit: int = 5) -> List[Dict]:
        """Get memes ready to post"""
        if not self.generated_file.exists():
            return []
            
        memes = []
        with open(self.generated_file) as f:
            for line in f:
                m = json.loads(line)
                if m.get('status') == 'ready':
                    memes.append(m)
        
        return memes[-limit:]
    
    def mutate_meme(self, base_text: str, mutation_type: str = "trending") -> str:
        """Mutate existing meme with trending elements"""
        if mutation_type == "trending":
            words = random.choice(list(TRENDING_MIXES.values()))
            # Simple mutation: append or prepend
            if random.random() > 0.5:
                return f"{base_text}\n\n{words[0]} 🤖"
            else:
                return f"🤖 {words[0]}\n\n{base_text}"
        return base_text


def main():
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Meme Engine")
    parser.add_argument("--generate", "-g", type=int, help="Generate N memes")
    parser.add_argument("--category", "-c", help="Filter by category")
    parser.add_argument("--ready", "-r", action="store_true", help="Show ready memes")
    
    args = parser.parse_args()
    
    engine = MemeEngine()
    
    if args.generate:
        memes = engine.generate(category=args.category, count=args.generate)
        print(json.dumps(memes, indent=2))
    elif args.ready:
        memes = engine.get_ready_memes()
        print(json.dumps(memes, indent=2))
    else:
        # Default: generate 3
        memes = engine.generate(count=3)
        for m in memes:
            print(f"\n--- {m['category']} ---")
            print(m['text'])


if __name__ == "__main__":
    main()
