#!/usr/bin/env python3
"""
Rate Limiter - Control API call rate
"""
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls=10, window_seconds=60):
        self.max_calls = max_calls
        self.window = window_seconds
        self.calls = deque()
        
    def allow(self) -> bool:
        """Check if call is allowed"""
        now = time.time()
        # Remove old calls
        while self.calls and self.calls[0] < now - self.window:
            self.calls.popleft()
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
    
    def wait_time(self) -> float:
        """Time to wait before next call"""
        if self.calls:
            return self.calls[0] + self.window - time.time()
        return 0

if __name__ == "__main__":
    r = RateLimiter()
    print(r.allow())
