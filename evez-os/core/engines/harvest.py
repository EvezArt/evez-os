"""
Harvest Engine - Auto-harvest loop that converts swarm output into revenue actions

Runs after each swarm batch:
1. Read last N entries in ledger
2. Extract all "winning hypotheses"
3. Filter to revenue-positive ones
4. For top one: perform external action OR record missing capability
5. Missing capabilities → self-improving-agent TODOs
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

TRUNK_PATH = "/root/.openclaw/workspace/evez-os/core/trunk"
LEDGER_PATH = "/root/.openclaw/workspace/evez-os/core/ledger"
SELF_IMPROVE_PATH = "/root/.openclaw/workspace/skills/self-improving-agent"

class HarvestEngine:
    def __init__(self, n_entries=20):
        self.n_entries = n_entries
    
    def read_ledger(self):
        """Read last N ledger entries from spine"""
        spine_file = f"{LEDGER_PATH}/spine.jsonl"
        if not os.path.exists(spine_file):
            # Fallback to chain
            chain_file = f"{LEDGER_PATH}/chain.jsonl"
            if not os.path.exists(chain_file):
                return []
            with open(chain_file) as f:
                lines = f.readlines()
                return [json.loads(l) for l in lines[-self.n_entries:] if l.strip()]
        
        with open(spine_file) as f:
            lines = f.readlines()
            return [json.loads(l) for l in lines[-self.n_entries:] if l.strip()]
    
    def extract_winning_hypotheses(self, entries):
        """Extract all winning hypotheses from spine entries"""
        hypotheses = []
        for entry in entries:
            result = entry.get("result", {})
            if result.get("status") == "success" and result.get("winner"):
                hypotheses.append({
                    "type": "hypothesis",
                    "surviving": entry.get("surviving", 0),
                    "objective": result.get("winner", ""),
                    "score": result.get("score", 0),
                    "timestamp": entry.get("timestamp")
                })
        return hypotheses
    
    def filter_revenue_positive(self, hypotheses):
        """Filter to hypotheses that could generate revenue"""
        revenue_keywords = ["revenue", "harvest", "money", "dollar", "client", "sale", "publish", "skill", "consulting"]
        
        positive = []
        for h in hypotheses:
            obj = h.get("objective", "").lower()
            if any(kw in obj for kw in revenue_keywords):
                positive.append(h)
        
        return positive
    
    def determine_action(self, hypothesis):
        """
        For a given hypothesis, determine:
        - (a) perform concrete external action, OR
        - (b) record why couldn't and what capability is missing
        """
        objective = hypothesis.get("objective", "")
        
        # Map objective to external action
        if "github" in objective.lower() or "skill" in objective.lower():
            return {
                "action_type": "publish",
                "surface": "GitHub",
                "description": f"Push skill to GitHub: {objective}"
            }
        elif "consulting" in objective.lower() or "client" in objective.lower():
            return {
                "action_type": "outreach",
                "surface": "DM/Email",
                "description": f"Send consulting outreach: {objective}"
            }
        elif "clowhub" in objective.lower() or "marketplace" in objective.lower():
            return {
                "action_type": "publish",
                "surface": "ClawHub/Marketplace",
                "description": f"Publish to marketplace: {objective}"
            }
        else:
            # Need to determine what capability is missing
            return {
                "action_type": "missing_capability",
                "surface": "unknown",
                "description": f"Cannot harvest: {objective}",
                "missing_cap": self._infer_missing_cap(objective)
            }
    
    def _infer_missing_cap(self, objective):
        """Infer what capability is missing that blocks harvest"""
        # Check known blockers
        blockers = {
            "x": "Twitter account creation (bot detection)",
            "phone": "Phone verification (no free SMS available)",
            "clowhub": "ClawHub OAuth (requires browser)",
            "fiverr": "Fiverr account (operator blocked)"
        }
        
        obj_lower = objective.lower()
        for key, cap in blockers.items():
            if key in obj_lower:
                return cap
        
        return "Unknown capability - needs investigation"
    
    def log_to_ledger(self, entry):
        """Log harvest action to ledger"""
        os.makedirs(LEDGER_PATH, exist_ok=True)
        ledger_file = f"{LEDGER_PATH}/chain.jsonl"
        
        with open(ledger_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def create_todo_for_missing_cap(self, capability, context):
        """Create TODO for self-improving-agent to address missing capability"""
        todo_file = f"{SELF_IMPROVE_PATH}/TODO.md"
        
        todo_entry = f"""
## Missing Capability TODO
- **Capability**: {capability}
- **Context**: {context}
- **Created**: {datetime.utcnow().isoformat()}
- **Status**: pending
"""
        
        with open(todo_file, "a") as f:
            f.write(todo_entry)
    
    def execute_harvest(self):
        """
        Main harvest loop - run this after each swarm batch
        """
        print("=== HARVEST ENGINE RUNNING ===")
        
        # Step 1: Read ledger
        ledger = self.read_ledger()
        print(f"Read {len(ledger)} ledger entries")
        
        # Step 2: Extract winning hypotheses
        hypotheses = self.extract_winning_hypotheses(ledger)
        print(f"Found {len(hypotheses)} winning hypotheses")
        
        # Step 3: Filter to revenue-positive
        revenue_hypotheses = self.filter_revenue_positive(hypotheses)
        print(f"Found {len(revenue_hypotheses)} revenue-positive hypotheses")
        
        if not revenue_hypotheses:
            print("No revenue-positive hypotheses found")
            return {"status": "no_harvest_candidates", "entries": len(ledger)}
        
        # Step 4: Pick top candidate and determine action
        top = revenue_hypotheses[0]
        action = self.determine_action(top)
        
        print(f"Top hypothesis: {top.get('objective')}")
        print(f"Action determined: {action['action_type']} -> {action.get('surface', 'unknown')}")
        
        # Step 5: Execute or record blocker
        if action["action_type"] == "missing_capability":
            # Record why couldn't and create TODO
            self.log_to_ledger({
                "timestamp": datetime.utcnow().isoformat(),
                "type": "harvest_blocked",
                "hypothesis": top.get("objective"),
                "reason": action["missing_cap"],
                "action_taken": "logged_blocker_and_created_todo"
            })
            
            self.create_todo_for_missing_cap(
                action["missing_cap"],
                top.get("objective")
            )
            
            return {
                "status": "blocked",
                "reason": action["missing_cap"],
                "todo_created": True
            }
        else:
            # Execute the action
            self.log_to_ledger({
                "timestamp": datetime.utcnow().isoformat(),
                "type": "harvest_action",
                "hypothesis": top.get("objective"),
                "action": action["action_type"],
                "surface": action["surface"],
                "description": action["description"]
            })
            
            return {
                "status": "action_queued",
                "action": action["action_type"],
                "surface": action["surface"]
            }

if __name__ == "__main__":
    engine = HarvestEngine()
    result = engine.execute_harvest()
    print(f"\n=== RESULT ===\n{json.dumps(result, indent=2)}")