"""
Kilo-to-EVEZ Bridge - Organism Protocol

Every Kilo agent gets:
1. Current trunk snapshot
2. Last K spine entries
3. Agency's job queue slice

In return, it must emit a structured "hypothesis + proposed action" payload
into EVEZ-OS via this bridge, which writes to ledger/chain.jsonl
as "external-cortex results", tagged by model and tool use.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

TRUNK_PATH = "/root/.openclaw/workspace/evez-os/core/trunk"
LEDGER_PATH = "/root/.openclaw/workspace/evez-os/core/ledger"

def load_trunk():
    """Load current trunk state"""
    with open(f"{TRUNK_PATH}/state.json") as f:
        return json.load(f)

def load_contract():
    """Load hard constraints"""
    with open(f"{TRUNK_PATH}/contract.json") as f:
        return json.load(f)

def load_ledger(k=20):
    """Load last K ledger entries"""
    ledger_file = f"{LEDGER_PATH}/chain.jsonl"
    if not os.path.exists(ledger_file):
        return []
    
    with open(ledger_file) as f:
        lines = f.readlines()
        return [json.loads(l) for l in lines[-k:] if l.strip()]

def load_agency_queue(agency_id):
    """Load job queue for specific agency"""
    # For now, read from contract's agency definitions
    contract = load_contract()
    return contract.get("agencies", {}).get(agency_id, {})

def create_agent_context(agent_id, agency_id=None):
    """
    Create context package for a Kilo agent
    
    Returns:
    {
        trunk_snapshot: {...},
        spine_entries: [...],
        agency_queue: {...},
        contract: {...}
    }
    """
    trunk = load_trunk()
    contract = load_contract()
    spine = load_ledger(20)
    agency_queue = load_agency_queue(agency_id) if agency_id else {}
    
    return {
        "trunk_snapshot": {
            "objective": trunk.get("trunk_objective", trunk.get("objective")),
            "current_mode": contract.get("current_mode"),
            "harvest_tracking": contract.get("harvest_tracking"),
            "play_mode": contract.get("play_modes", {}).get(contract.get("current_mode", "harvest"))
        },
        "spine_entries": spine[-10:],  # Last 10 entries
        "agency_queue": agency_queue,
        "contract_hard_constraints": contract.get("hard_constraints", {}),
        "timestamp": datetime.utcnow().isoformat()
    }

def write_agent_result(agent_id, payload):
    """
    Write agent result to ledger
    
    Payload must contain:
    {
        hypothesis: "string",
        proposed_action: "string",
        expected_value_usd: number (optional),
        model_used: "string" (optional),
        tool_used: "string" (optional)
    }
    """
    os.makedirs(LEDGER_PATH, exist_ok=True)
    ledger_file = f"{LEDGER_PATH}/chain.jsonl"
    
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": "external_cortex_result",
        "agent_id": agent_id,
        "hypothesis": payload.get("hypothesis"),
        "proposed_action": payload.get("proposed_action"),
        "expected_value_usd": payload.get("expected_value_usd"),
        "model_used": payload.get("model_used", "unknown"),
        "tool_used": payload.get("tool_used", "unknown"),
        "status": "pending_execution"
    }
    
    with open(ledger_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    return entry

# CLI interface for Kilo agents
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  bridge.py context <agent_id> [agency]  - Get context for agent")
        print("  bridge.py emit <agent_id> <payload_json> - Emit result to ledger")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "context":
        agent_id = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        agency = sys.argv[3] if len(sys.argv) > 3 else None
        ctx = create_agent_context(agent_id, agency)
        print(json.dumps(ctx, indent=2))
    
    elif command == "emit":
        if len(sys.argv) < 4:
            print("Error: need agent_id and payload")
            sys.exit(1)
        agent_id = sys.argv[2]
        payload = json.loads(sys.argv[3])
        result = write_agent_result(agent_id, payload)
        print(json.dumps(result, indent=2))