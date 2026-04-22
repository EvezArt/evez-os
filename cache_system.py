#!/usr/bin/env python3
"""
Cache System - Cache API calls and computations
"""
import json
import hashlib
from pathlib import Path

class CacheSystem:
    def __init__(self, cache_dir="/tmp/kiloclaw_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def key(self, data):
        """Generate cache key"""
        return hashlib.md5(json.dumps(data).encode()).hexdigest()
    
    def get(self, key):
        """Get cached value"""
        f = self.cache_dir / f"{key}.json"
        if f.exists():
            return json.loads(f.read_text())
        return None
    
    def set(self, key, value):
        """Set cached value"""
        f = self.cache_dir / f"{key}.json"
        f.write_text(json.dumps(value))
        
    def invalidate(self, key):
        """Clear cache entry"""
        f = self.cache_dir / f"{key}.json"
        if f.exists():
            f.unlink()

if __name__ == "__main__":
    c = CacheSystem()
    c.set("test", {"data": "value"})
    print(c.get("test"))
