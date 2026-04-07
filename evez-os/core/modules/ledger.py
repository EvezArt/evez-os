"""
EVEZ-OS Ledger
Immutable event log with cryptographic chain
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

class EvezLedger:
    def __init__(self, ledger_path):
        self.ledger_path = Path(ledger_path)
        self.ledger_path.mkdir(parents=True, exist_ok=True)
        self.spine_file = self.ledger_path / "spine.jsonl"
        self.chain_file = self.ledger_path / "chain.jsonl"
        self.last_hash = None
        
    def init(self):
        """Initialize ledger"""
        # Create genesis block
        genesis = {
            "index": 0,
            "timestamp": datetime.utcnow().isoformat(),
            "data": "EVEZ-OS GENESIS",
            "prev_hash": "0" * 64,
            "hash": self._hash_block(0, "EVEZ-OS GENESIS", "0" * 64)
        }
        
        with open(self.chain_file, "w") as f:
            f.write(json.dumps(genesis) + "\n")
            
        self.last_hash = genesis["hash"]
        
    def _hash_block(self, index, data, prev_hash):
        """Calculate hash for block"""
        content = f"{index}{data}{prev_hash}{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()
        
    def record(self, event):
        """Record event to spine and chain"""
        # Add to spine (append-only log)
        event["timestamp"] = datetime.utcnow().isoformat()
        with open(self.spine_file, "a") as f:
            f.write(json.dumps(event) + "\n")
            
        # Add to chain (cryptographic)
        block = {
            "index": self._get_chain_length(),
            "timestamp": datetime.utcnow().isoformat(),
            "data": json.dumps(event),
            "prev_hash": self.last_hash,
            "hash": ""
        }
        block["hash"] = self._hash_block(block["index"], block["data"], block["prev_hash"])
        
        with open(self.chain_file, "a") as f:
            f.write(json.dumps(block) + "\n")
            
        self.last_hash = block["hash"]
        
    def _get_chain_length(self):
        """Get current chain length"""
        if not self.chain_file.exists():
            return 0
        with open(self.chain_file) as f:
            return sum(1 for _ in f)
            
    def get_spine(self, limit=100):
        """Get recent spine events"""
        if not self.spine_file.exists():
            return []
            
        events = []
        with open(self.spine_file) as f:
            for line in f:
                events.append(json.loads(line))
                if len(events) >= limit:
                    break
        return events