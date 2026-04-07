#!/usr/bin/env python3
"""Generate a proof receipt from latest harvest cycle."""
import json
from datetime import datetime

LOG_FILE = "/root/.openclaw/workspace/evez-os/core/continuous_loop_log.jsonl"

def generate_receipt():
    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()
    
    if not lines:
        return None
    
    # Get last entry
    last = json.loads(lines[-1])
    
    receipt = {
        "receipt_id": f"RECEIPT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "event_count": last.get("state", {}).get("ledger_events", 0),
        "objective": last.get("state", {}).get("current_objective", "unknown"),
        "last_action": last.get("action", {}).get("action", "unknown"),
        "success": last.get("result", {}).get("success", False),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return receipt

if __name__ == "__main__":
    r = generate_receipt()
    print(json.dumps(r, indent=2))
