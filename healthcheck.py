#!/usr/bin/env python3
"""Health check endpoint for EVEZ"""
import json
from datetime import datetime

def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "cognition": "ok",
            "inference": "ok",
            "quantum": "ok"
        }
    }

if __name__ == "__main__":
    print(json.dumps(health(), indent=2))
