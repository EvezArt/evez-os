#!/usr/bin/env python3
"""
EVEZ Context Bridge
Connects Short-Term Context (STM) and Long-Term Context (LTM)

On every decision:
  1. READ LTM for relevant history
  2. DECIDE in STM  
  3. COMMIT to both layers

On session start:
  1. Load MEMORY.md (long-term)
  2. Load today's notes (short-term)
  3. Reconcile with trunk objective

On session end:
  1. EXTRACT from STM → daily notes
  2. SUMMARIZE → MEMORY.md if significant
  3. APPEND → ledger (immutable)
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

WORKSPACE = Path("/root/.openclaw/workspace")
EVEZ_CORE = WORKSPACE / "evez-os" / "core"
CONTEXT_DIR = EVEZ_CORE / "context"
LEDGER_DIR = EVEZ_CORE / "ledger"
TRUNK_DIR = EVEZ_CORE / "trunk"


class ContextBridge:
    """Bridge between STM and LTM"""
    
    def __init__(self):
        CONTEXT_DIR.mkdir(exist_ok=True)
        self.stm_file = CONTEXT_DIR / "stm.json"
        self.ltm_index = CONTEXT_DIR / "ltm_index.json"
        
    # === STM OPERATIONS ===
    
    def load_stm(self) -> Dict:
        """Load short-term context"""
        if self.stm_file.exists():
            with open(self.stm_file) as f:
                return json.load(f)
        return {
            "session_start": datetime.utcnow().isoformat(),
            "current_objective": None,
            "pending_actions": [],
            "recent_decisions": [],
            "context_stack": []
        }
    
    def save_stm(self, stm: Dict):
        """Save short-term context"""
        with open(self.stm_file, "w") as f:
            json.dump(stm, f, indent=2)
    
    def set_objective(self, objective: str):
        """Set current objective in STM"""
        stm = self.load_stm()
        stm["current_objective"] = objective
        stm["objective_set_at"] = datetime.utcnow().isoformat()
        self.save_stm(stm)
    
    def push_context(self, key: str, value: Any):
        """Push context to STM stack"""
        stm = self.load_stm()
        stm["context_stack"].append({
            "key": key,
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.save_stm(stm)
    
    # === LTM OPERATIONS ===
    
    def load_ltm_index(self) -> Dict:
        """Load LTM reference index"""
        if self.ltm_index.exists():
            with open(self.ltm_index) as f:
                return json.load(f)
        return {
            "memory_file": str(WORKSPACE / "MEMORY.md"),
            "ledger_files": {
                "spine": str(LEDGER_DIR / "spine.jsonl"),
                "chain": str(LEDGER_DIR / "chain.jsonl")
            },
            "last_sync": None
        }
    
    def read_memory(self) -> str:
        """Read long-term memory (MEMORY.md)"""
        mem_file = WORKSPACE / "MEMORY.md"
        if mem_file.exists():
            with open(mem_file) as f:
                return f.read()
        return ""
    
    def append_to_memory(self, entry: str):
        """Append to MEMORY.md"""
        mem_file = WORKSPACE / "MEMORY.md"
        with open(mem_file, "a") as f:
            f.write(f"\n\n## {datetime.utcnow().strftime('%Y-%m-%d')}\n{entry}")
    
    # === LEDGER OPERATIONS ===
    
    def append_ledger(self, event_type: str, data: Dict):
        """Append to immutable ledger"""
        spine = LEDGER_DIR / "spine.jsonl"
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            **data
        }
        with open(spine, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        # Update LTM index
        ltm = self.load_ltm_index()
        ltm["last_sync"] = datetime.utcnow().isoformat()
        with open(self.ltm_index, "w") as f:
            json.dump(ltm, f, indent=2)
    
    def read_ledger_recent(self, hours: int = 24) -> List[Dict]:
        """Read recent ledger entries"""
        spine = LEDGER_DIR / "spine.jsonl"
        if not spine.exists():
            return []
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        results = []
        
        with open(spine) as f:
            for line in f:
                entry = json.loads(line)
                entry_time = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                if entry_time.replace(tzinfo=None) > cutoff:
                    results.append(entry)
        return results
    
    # === TRUNK OPERATIONS ===
    
    def load_trunk(self) -> Dict:
        """Load trunk state"""
        trunk_file = TRUNK_DIR / "state.json"
        if trunk_file.exists():
            with open(trunk_file) as f:
                return json.load(f)
        return {"objective": None, "branches": []}
    
    def save_trunk(self, trunk: Dict):
        """Save trunk state"""
        trunk_file = TRUNK_DIR / "state.json"
        with open(trunk_file, "w") as f:
            json.dump(trunk, f, indent=2)
    
    # === FULL CONTEXT LOAD ===
    
    def load_full_context(self) -> Dict:
        """Load complete context from all layers"""
        return {
            "stm": self.load_stm(),
            "trunk": self.load_trunk(),
            "ltm_summary": self.read_memory()[:2000],  # First 2k chars
            "recent_ledger": self.read_ledger_recent(hours=24),
            "loaded_at": datetime.utcnow().isoformat()
        }
    
    # === DECISION COMMIT ===
    
    def commit_decision(self, decision: str, rationale: str, outcome: str = None):
        """Commit a decision to both STM and LTM"""
        # STM: Add to recent decisions
        stm = self.load_stm()
        stm["recent_decisions"].append({
            "decision": decision,
            "rationale": rationale,
            "outcome": outcome,
            "timestamp": datetime.utcnow().isoformat()
        })
        # Keep only last 10
        stm["recent_decisions"] = stm["recent_decisions"][-10:]
        self.save_stm(stm)
        
        # LTM: Append to ledger
        self.append_ledger("decision", {
            "decision": decision,
            "rationale": rationale,
            "outcome": outcome
        })
        
        # LTM: Optionally add to memory if significant
        if outcome and "success" in outcome.lower():
            self.append_to_memory(f"Decision '{decision}' resulted in: {outcome}")


if __name__ == "__main__":
    # Test
    bridge = ContextBridge()
    ctx = bridge.load_full_context()
    print("=== CONTEXT BRIDGE TEST ===")
    print(f"STM keys: {list(ctx['stm'].keys())}")
    print(f"Trunk objective: {ctx['trunk'].get('objective')}")
    print(f"Recent ledger entries: {len(ctx['recent_ledger'])}")
    
    # Commit test decision
    bridge.commit_decision(
        decision="Test context bridge",
        rationale="Testing the new system",
        outcome="Works"
    )
    print("Test decision committed.")
