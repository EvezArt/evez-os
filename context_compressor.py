#!/usr/bin/env python3
"""
Context Compressor - Compress conversation history
"""
import json

class ContextCompressor:
    def __init__(self):
        self.history = []
        
    def compress(self, messages, max_tokens=4000):
        """Compress messages to fit token budget"""
        compressed = []
        for msg in messages[-10:]:
            # Keep last messages, compress older ones
            text = msg.get("content", "")[:100]
            compressed.append({"role": msg.get("role"), "content": text})
        return {"messages": compressed, "count": len(compressed)}
    
    def summarize(self, messages):
        """Summarize conversation flow"""
        topics = [m.get("content", "")[:30] for m in messages[-5:]]
        return {"topics": topics, "count": len(topics)}

if __name__ == "__main__":
    c = ContextCompressor()
    print(c.compress([{"role": "user", "content": "Hello"}]))
