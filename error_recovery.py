#!/usr/bin/env python3
"""
Error Recovery - Auto-retry failed operations
"""
import time

class ErrorRecovery:
    def __init__(self):
        self.max_retries = 3
        
    def retry(self, func, *args, **kwargs):
        """Retry function with backoff"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                wait = 2 ** attempt
                time.sleep(wait)
        return {"error": "max_retries"}
    
    def circuit_breaker(self, failures):
        """Circuit breaker pattern"""
        if failures > 5:
            return {"status": "open"}
        return {"status": "closed"}

if __name__ == "__main__":
    e = ErrorRecovery()
    print(e.retry(lambda: "success"))
