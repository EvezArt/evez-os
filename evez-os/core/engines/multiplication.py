"""
Multiplication Engine - Operationalizes the intelligence formula

M = log(1 + tool_span × skill_span) + α × parallelism + β × self_improve_events
"""

import json
import os
from datetime import datetime, timedelta

TRUNK_PATH = "/root/.openclaw/workspace/evez-os/core/trunk"
LEDGER_PATH = "/root/.openclaw/workspace/evez-os/core/ledger"

ALPHA = 0.5  # parallelism weight
BETA = 1.0   # self-improvement weight

def get_current_state():
    """Load current trunk state"""
    with open(f"{TRUNK_PATH}/state.json") as f:
        return json.load(f)

def get_contract():
    """Load hard constraints contract"""
    with open(f"{TRUNK_PATH}/contract.json") as f:
        return json.load(f)

def get_recent_ledger(n=20):
    """Get last N ledger entries"""
    ledger_file = f"{LEDGER_PATH}/chain.jsonl"
    if not os.path.exists(ledger_file):
        return []
    with open(ledger_file) as f:
        lines = f.readlines()
        return [json.loads(l) for l in lines[-n:] if l.strip()]

def compute_tool_span(ledger_entries):
    """Count distinct external tools used in last N steps"""
    tools = set()
    for entry in ledger_entries:
        if "tool_used" in entry:
            tools.add(entry["tool_used"])
        if "tools" in entry:
            tools.update(entry["tools"])
    return len(tools)

def compute_skill_span(ledger_entries):
    """Count distinct skills invoked in last N steps"""
    skills = set()
    for entry in ledger_entries:
        if "skill" in entry:
            skills.add(entry["skill"])
    return len(skills)

def compute_parallelism():
    """Count currently active parallel agents"""
    # Could check Kilo/OpenClaw session count
    # For now, return from contract or default
    state = get_current_state()
    return state.get("CURRENT_METRICS", {}).get("parallelism", 1)

def compute_self_improve_events(ledger_entries):
    """Count self-improvement events in recent history"""
    count = 0
    for entry in ledger_entries:
        if entry.get("type") == "self_improve" or "improvement" in entry.get("delta", "").lower():
            count += 1
    return count

def compute_multiplication_score():
    """Compute M score for current system state"""
    ledger = get_recent_ledger(20)
    
    tool_span = compute_tool_span(ledger)
    skill_span = compute_skill_span(ledger)
    parallelism = compute_parallelism()
    self_improve = compute_self_improve_events(ledger)
    
    M = (tool_span * skill_span) + (ALPHA * parallelism) + (BETA * self_improve)
    
    return {
        "M": round(M, 3),
        "tool_span": tool_span,
        "skill_span": skill_span,
        "parallelism": parallelism,
        "self_improve_events": self_improve,
        "timestamp": datetime.utcnow().isoformat()
    }

def is_compliant(branch_proposal):
    """
    Check if a branch proposal is contract-compliant.
    
    A branch must either:
    1. Increment harvest_count, OR
    2. Increment skill_assets, OR  
    3. Increment revenue_usd (mrr_proxy), OR
    4. If purely research (no revenue), must be balanced by harvest branch within N cycles
    """
    contract = get_contract()
    constraints = contract["hard_constraints"]
    
    move_type = branch_proposal.get("move_type", "unknown")
    
    # Research-only branches are allowed but must be balanced
    if move_type == "research":
        if contract.get("play_modes", {}).get("explore", {}).get("allow_research_only"):
            return {
                "compliant": True,
                "requires_balance": True,
                "counter_balance_in_cycles": contract["play_modes"]["explore"]["counter_balance_harvest_every_n_cycles"]
            }
    
    # Revenue branches must increment at least one metric
    revenue_moves = constraints["must_increment"]
    for metric in revenue_moves:
        if branch_proposal.get(metric):
            return {"compliant": True, "requires_balance": False}
    
    return {
        "compliant": False,
        "reason": f"Branch does not increment any of: {revenue_moves}"
    }

def get_mission():
    """
    Generate current mission based on play mode and contract.
    
    Returns the primary objective considering:
    - Current mode (harvest vs explore)
    - Contract constraints
    - Current metrics
    """
    contract = get_contract()
    state = get_current_state()
    
    mode = contract.get("current_mode", "harvest")
    harvest_tracking = contract["harvest_tracking"]
    
    if mode == "harvest":
        return {
            "mode": "harvest",
            "objective": f"Close at least 1 revenue transaction. Current: {harvest_tracking['harvest_count']} harvests, ${harvest_tracking['mrr_proxy_cents']/100:.2f} MRR proxy",
            "priority": "revenue",
            "timeout_hours": contract["play_modes"]["harvest"]["timeout_hours"]
        }
    else:
        return {
            "mode": "explore",
            "objective": "Maximize M score (multiplication) without decreasing harvest_count",
            "priority": "multiplication",
            "constraints": f"Maintain min {contract['hard_constraints']['harvest_count_min']} harvests, {contract['hard_constraints']['skill_assets_min']} skills"
        }

if __name__ == "__main__":
    M = compute_multiplication_score()
    print(f"Multiplication Score: {M}")
    print(f"Mission: {get_mission()}")