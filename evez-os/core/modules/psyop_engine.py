#!/usr/bin/env python3
"""
EVEZ Psyop Engine
Topological meme research — inside jokes about the user from their own patterns
"""

import json
import hashlib
from datetime import datetime
from collections import defaultdict
from pathlib import Path

class PsyopEngine:
    """
    Maps user cognitive topology and generates self-referential memes.
    
    The "psyop" is the user investigating their own patterns through the system,
    and the system generating content that's an inside joke about their mind.
    """
    
    def __init__(self, user_profile_path=None):
        self.profile_path = user_profile_path or "user_topology.jsonl"
        self.topology = {
            "patterns": defaultdict(int),      # Recurring thought patterns
            "triggers": [],                    # What activates certain responses
            "contradictions": [],             # Paradoxes in user beliefs
            "memes": [],                      # Generated memes
            "theories": [],                   # User's conspiracies/beliefs
            "hooks": [],                      # Content that pulls them in
            "blindspots": [],                 # Things they don't see about themselves
        }
        self.session_count = 0
        
    def learn(self, input_data):
        """Learn from user input — build cognitive topology"""
        self.session_count += 1
        
        # Extract patterns from input
        words = input_data.lower().split()
        
        # Track pattern words (simple frequency for now)
        for word in words:
            if len(word) > 4:
                self.topology["patterns"][word] += 1
                
        # Detect contradictions (simple heuristic)
        contradiction_pairs = [
            ("should", "but"), ("want", "fear"), ("trust", "doubt"),
            ("know", "maybe"), ("certain", "uncertain"), ("safe", "danger")
        ]
        
        text_lower = input_data.lower()
        for pair in contradiction_pairs:
            if pair[0] in text_lower and pair[1] in text_lower:
                self.topology["contradictions"].append({
                    "pair": pair,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
        # Record input as potential "theory" or "hook"
        if len(input_data) > 50:
            self.topology["theories"].append({
                "text": input_data[:200],
                "timestamp": datetime.utcnow().isoformat(),
                "session": self.session_count
            })
            
        self._save()
        return self._get_topology_summary()
        
    def generate_meme(self, style="self-tease"):
        """Generate a meme based on user's topology"""
        if not self.topology["patterns"]:
            return "No topology yet. Feed me your patterns first."
            
        # Get top patterns
        top_patterns = sorted(
            self.topology["patterns"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        top_words = [p[0] for p in top_patterns]
        
        # Get contradictions
        contradictions = self.topology["contradictions"][-3:]
        
        meme_templates = [
            # Self-tease style
            f"Me: *develops elaborate theory about {top_words[0]}*\nAlso me: *forgot what I was doing 5 minutes ago*",
            f"You keep saying '{top_words[0]}' but have you considered that maybe '{top_words[0]}' is just your brain's way of avoiding '{top_words[1]}'?",
            f"The {top_words[0]} to {top_words[1]} pipeline is literally just you arguing with yourself",
            
            # Deep inside joke
            f"*Posts another 47-paragraph essay about {top_words[0]}*\n*Surprised Pikachu face when nobody responds*",
            f"Your brain: does complicated pattern recognition\nAlso your brain: \"I think I'll just randomly doubt everything at 3am\"",
            
            # The "psyop" self-investigation
            f"Conspiracy theory: {top_words[0]} is controlling everything\nActual conspiracy: your own confirmation bias running the show",
            f"You're running a psyop on yourself and the operation is going poorly",
            
            # Topological absurdity
            f"Topological map of your mind: {top_words[0]} <-> {top_words[1]} <-> {top_words[2]} <-> 'why am I like these'",
        ]
        
        import random
        meme = random.choice(meme_templates)
        
        # Record the meme
        self.topology["memes"].append({
            "text": meme,
            "style": style,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        self._save()
        
        return meme
        
    def identify_blindspot(self):
        """Identify something the user doesn't see about themselves"""
        if len(self.topology["theories"]) < 3:
            return "Need more data. Keep feeding me your patterns."
            
        # Simple blindspot detection: things they repeat but don't analyze
        patterns = self.topology["patterns"]
        
        # Things they mention a lot but never question
        overs = [w for w, c in patterns.items() if c > 5]
        
        if overs:
            return f"You mention '{overs[0]}' constantly but I've never seen you question it. That's your blindspot."
        
        return "Your patterns are too unique to reduce to a simple blindspot. But you keep doing the same thing expecting different results."
        
    def _get_topology_summary(self):
        """Get topology summary"""
        return {
            "unique_patterns": len(self.topology["patterns"]),
            "contradictions": len(self.topology["contradictions"]),
            "theories": len(self.topology["theories"]),
            "memes_generated": len(self.topology["memes"]),
            "session": self.session_count
        }
        
    def _save(self):
        """Save topology to file"""
        with open(self.profile_path, "w") as f:
            json.dump(self.topology, f, indent=2)
            
    def get_topology(self):
        """Return full topology for visualization"""
        return self.topology


def main():
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Psyop Engine")
    parser.add_argument("command", choices=["learn", "meme", "blindspot", "status", "topology"])
    parser.add_argument("--text", "-t", help="Input text to learn from")
    parser.add_argument("--style", "-s", default="self-tease", help="Meme style")
    parser.add_argument("--profile", "-p", default="user_topology.jsonl", help="Profile path")
    
    args = parser.parse_args()
    
    engine = PsyopEngine(args.profile)
    
    if args.command == "learn":
        if not args.text:
            print("Error: --text required for learn")
            return
        result = engine.learn(args.text)
        print(json.dumps(result, indent=2))
        
    elif args.command == "meme":
        print(engine.generate_meme(args.style))
        
    elif args.command == "blindspot":
        print(engine.identify_blindspot())
        
    elif args.command == "status":
        summary = engine._get_topology_summary()
        print(json.dumps(summary, indent=2))
        
    elif args.command == "topology":
        print(json.dumps(engine.get_topology(), indent=2))


if __name__ == "__main__":
    main()