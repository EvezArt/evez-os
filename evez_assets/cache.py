#!/usr/bin/env python3
"""
EVEZ Cache - Caching, memoization, TTL management
Performance optimization via intelligent caching
"""

import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CacheEntry:
    key: str
    value: Any
    created: float
    expires: float
    hits: int = 0

class CacheEngine:
    """EVEZ Cache - Intelligent caching system"""
    
    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            self.stats["misses"] += 1
            return None
        
        entry = self.cache[key]
        
        # Check expiration
        if time.time() > entry.expires:
            del self.cache[key]
            self.stats["misses"] += 1
            return None
        
        # Update hits
        entry.hits += 1
        self.stats["hits"] += 1
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        self.cache[key] = CacheEntry(
            key=key,
            value=value,
            created=time.time(),
            expires=time.time() + ttl
        )
    
    def delete(self, key: str) -> bool:
        """Delete from cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self):
        """Clear all cache"""
        count = len(self.cache)
        self.cache.clear()
        self.stats["evictions"] += count
    
    def get_or_compute(self, key: str, compute_fn: Callable, ttl: Optional[int] = None) -> Any:
        """Get from cache or compute and cache"""
        value = self.get(key)
        if value is not None:
            return value
        
        # Compute
        value = compute_fn()
        self.set(key, value, ttl)
        return value
    
    def memoize(self, fn: Callable) -> Callable:
        """Decorator to memoize a function"""
        def wrapper(*args, **kwargs):
            key = f"{fn.__name__}:{str(args)}:{str(kwargs)}"
            return self.get_or_compute(key, lambda: fn(*args, **kwargs))
        return wrapper
    
    def cleanup(self) -> int:
        """Remove expired entries"""
        now = time.time()
        expired = [k for k, v in self.cache.items() if now > v.expires]
        
        for k in expired:
            del self.cache[k]
        
        self.stats["evictions"] += len(expired)
        return len(expired)
    
    def get_stats(self) -> Dict:
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0
        
        return {
            "entries": len(self.cache),
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "evictions": self.stats["evictions"]
        }


# Demo
if __name__ == "__main__":
    cache = CacheEngine(ttl=60)
    print("=== EVEZ Cache ===")
    
    cache.set("key1", {"data": "value1"})
    print(f"Get key1: {cache.get('key1')}")
    print(f"Get key2: {cache.get('key2')}")  # Miss
    
    # Memoize function
    @cache.memoize
    def expensive_function(x):
        return x * x
    
    print(f"Memoized call: {expensive_function(5)}")
    print(f"Cache stats: {cache.get_stats()}")