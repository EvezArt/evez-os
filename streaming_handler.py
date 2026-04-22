#!/usr/bin/env python3
"""
Streaming Handler - Process streaming responses in real-time
"""
import json
import threading

class StreamingHandler:
    def __init__(self):
        self.buffer = ""
        
    def on_chunk(self, chunk):
        """Process each chunk"""
        self.buffer += chunk
        return {"chunk": chunk, "buffer_len": len(self.buffer)}
    
    def get_content(self):
        """Get current content"""
        return self.buffer
    
    def reset(self):
        """Reset buffer"""
        self.buffer = ""

if __name__ == "__main__":
    h = StreamingHandler()
    print(h.on_chunk("Hello "))
    print(h.on_chunk("World"))
