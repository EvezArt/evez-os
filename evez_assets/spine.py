#!/usr/bin/env python3
"""
EVEZ-Style Event Spine - Append-only event log with cryptographic integrity
Foundation for autonomous agent memory and decision tracking
"""

import json
import hashlib
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid

class EventSpine:
    """Append-only event spine with tamper-evident chain"""
    
    def __init__(self, path: str = "./spine.jsonl", create: bool = True):
        self.path = Path(path)
        self.chain = []
        self.last_hash = "0" * 64
        
        if create and not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._init_genesis()
        elif self.path.exists():
            self._load()
    
    def _init_genesis(self):
        """Create genesis block"""
        genesis = {
            "id": str(uuid.uuid4()),
            "type": "GENESIS",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {"message": "EVEZ-style event spine initialized"},
            "prev_hash": "0" * 64,
            "hash": self._compute_hash("GENESIS", {}, "0" * 64)
        }
        self.last_hash = genesis["hash"]
        self._append(genesis)
    
    def _compute_hash(self, event_type: str, data: Dict, prev_hash: str) -> str:
        content = f"{event_type}:{json.dumps(data, sort_keys=True)}:{prev_hash}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _append(self, event: Dict):
        with open(self.path, "a") as f:
            f.write(json.dumps(event) + "\n")
    
    def _load(self):
        """Load existing spine"""
        if not self.path.exists():
            return
        with open(self.path, "r") as f:
            for line in f:
                event = json.loads(line)
                self.chain.append(event)
                self.last_hash = event.get("hash", self.last_hash)
    
    def append(self, event_type: str, data: Dict, metadata: Optional[Dict] = None) -> Dict:
        """Append new event to spine"""
        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": data,
            "metadata": metadata or {},
            "prev_hash": self.last_hash,
            "hash": self._compute_hash(event_type, data, self.last_hash)
        }
        self.last_hash = event["hash"]
        self._append(event)
        self.chain.append(event)
        return event
    
    def verify(self) -> bool:
        """Verify spine integrity"""
        prev_hash = "0" * 64
        for event in self.chain:
            if event["type"] == "GENESIS":
                prev_hash = event["hash"]
                continue
            expected_hash = self._compute_hash(event["type"], event["data"], event["prev_hash"])
            if expected_hash != event["hash"]:
                return False
            prev_hash = event["hash"]
        return True
    
    def query(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Query events"""
        results = self.chain
        if event_type:
            results = [e for e in results if e["type"] == event_type]
        return results[-limit:]
    
    def get_state(self) -> Dict:
        """Get current spine state"""
        return {
            "length": len(self.chain),
            "last_hash": self.last_hash,
            "verified": self.verify(),
            "last_event": self.chain[-1] if self.chain else None
        }


# CLI
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Event Spine")
    parser.add_argument("command", choices=["init", "append", "query", "verify", "state"])
    parser.add_argument("--type", "-t", help="Event type")
    parser.add_argument("--data", "-d", help="JSON data")
    parser.add_argument("--path", "-p", default="./spine.jsonl", help="Spine path")
    args = parser.parse_args()
    
    spine = EventSpine(args.path)
    
    if args.command == "append":
        data = json.loads(args.data) if args.data else {}
        event = spine.append(args.type or "EVENT", data)
        print(json.dumps(event, indent=2))
    elif args.command == "query":
        for e in spine.query(args.type):
            print(json.dumps(e))
    elif args.command == "verify":
        print(f"Verified: {spine.verify()}")
    elif args.command == "state":
        print(json.dumps(spine.get_state(), indent=2))
    elif args.command == "init":
        print("Initialized")