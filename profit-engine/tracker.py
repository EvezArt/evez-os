#!/usr/bin/env python3
"""
Profit Engine - Cost & Revenue Tracker
Legitimate automation: track costs, find ROI opportunities, monitor revenue.
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path

LEDGER_PATH = Path(__file__).parent / "ledger.json"

def load_ledger():
    if LEDGER_PATH.exists():
        return json.loads(LEDGER_PATH.read_text())
    return {"instances": {}, "cycles": [], "opportunities": [], "config": {"min_roi_threshold": 1.0}}

def save_ledger(data):
    LEDGER_PATH.write_text(json.dumps(data, indent=2))

def log_cycle(instance_id: str, api_cost: float, compute_cost: float, external_cost: float = 0):
    """Log operational costs for one cycle."""
    data = load_ledger()
    total = api_cost + compute_cost + external_cost
    
    cycle = {
        "timestamp": datetime.utcnow().isoformat(),
        "instance": instance_id,
        "costs": {"api": api_cost, "compute": compute_cost, "external": external_cost, "total": total}
    }
    data["cycles"].append(cycle)
    save_ledger(data)
    return cycle

def log_opportunity(name: str, expected_revenue: float, cost: float, source: str, url: str = ""):
    """Add a legitimate opportunity."""
    data = load_ledger()
    roi = (expected_revenue - cost) / cost if cost > 0 else 0
    
    data["opportunities"].append({
        "name": name,
        "expected_revenue": expected_revenue,
        "cost": cost,
        "roi": roi,
        "source": source,
        "url": url,
        "timestamp": datetime.utcnow().isoformat()
    })
    data["opportunities"].sort(key=lambda x: x["roi"], reverse=True)
    save_ledger(data)
    return roi

def get_top_opportunities(min_roi: float = 1.0, limit: int = 5):
    """Get highest ROI legitimate opportunities."""
    data = load_ledger()
    valid = [o for o in data["opportunities"] if o["roi"] >= min_roi]
    return valid[:limit]

def get_total_costs():
    """Sum all logged costs."""
    data = load_ledger()
    total = {"api": 0, "compute": 0, "external": 0, "total": 0}
    for cycle in data["cycles"]:
        for k in total:
            total[k] += cycle["costs"].get(k, 0)
    return total

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: tracker.py <command> [args]")
        print("Commands: log-cycle, add-opp, top-opp, total-costs")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "log-cycle":
        # python tracker.py log-cycle <instance> <api_cost> <compute_cost>
        cycle = log_cycle(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
        print(f"Logged: {cycle}")
    elif cmd == "add-opp":
        # python tracker.py add-opp <name> <revenue> <cost> <source> [url]
        roi = log_opportunity(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5], sys.argv[6] if len(sys.argv) > 6 else "")
        print(f"Added opportunity (ROI: {roi:.2f})")
    elif cmd == "top-opp":
        for o in get_top_opportunities():
            print(f"{o['name']}: ROI={o['roi']:.2f} ({o['source']})")
    elif cmd == "total-costs":
        costs = get_total_costs()
        print(f"Total costs: {costs}")