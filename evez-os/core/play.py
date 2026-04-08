"""
Play Lever - Single human-level control for the organism

PLAY=harvest  → Aggressively prioritize closing revenue
PLAY=explore  → Maximize multiplication score M
"""

import json
import os
import sys

TRUNK_PATH = "/root/.openclaw/workspace/evez-os/core/trunk"
CONTRACT_PATH = f"{TRUNK_PATH}/contract.json"

def set_mode(mode):
    """Set play mode - 'harvest' or 'explore'"""
    if mode not in ["harvest", "explore"]:
        return {"error": f"Invalid mode: {mode}. Use 'harvest' or 'explore'"}
    
    with open(CONTRACT_PATH) as f:
        contract = json.load(f)
    
    contract["current_mode"] = mode
    contract["last_update"] = __import__("datetime").datetime.utcnow().isoformat()
    
    with open(CONTRACT_PATH, "w") as f:
        json.dump(contract, f, indent=2)
    
    return {
        "mode": mode,
        "status": "set",
        "mission": get_mission()
    }

def get_mode():
    """Get current play mode"""
    with open(CONTRACT_PATH) as f:
        contract = json.load(f)
    return contract.get("current_mode")

def get_mission():
    """Get current mission based on mode"""
    with open(CONTRACT_PATH) as f:
        contract = json.load(f)
    
    mode = contract.get("current_mode", "harvest")
    harvest_tracking = contract.get("harvest_tracking", {})
    play_config = contract.get("play_modes", {}).get(mode, {})
    
    if mode == "harvest":
        return {
            "mode": mode,
            "objective": f"Close at least {play_config.get('min_harvest_increment', 1)} revenue transaction",
            "timeout_hours": play_config.get("timeout_hours", 4),
            "current_stats": f"{harvest_tracking.get('harvest_count', 0)} harvests, ${harvest_tracking.get('mrr_proxy_cents', 0)/100:.2f} MRR"
        }
    else:
        return {
            "mode": mode,
            "objective": "Maximize M score without decreasing harvest_count",
            "constraint": f"Maintain min {contract['hard_constraints']['harvest_count_min']} harvests",
            "balance_every_n_cycles": play_config.get("counter_balance_harvest_every_n_cycles", 3)
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Current mode: {get_mode()}")
        print(f"\nMission: {json.dumps(get_mission(), indent=2)}")
        print("\nUsage:")
        print("  play.py harvest  - Set mode to harvest (aggressive revenue)")
        print("  play.py explore  - Set mode to explore (multiplication)")
        print("  play.py status  - Show current status")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "harvest":
        result = set_mode("harvest")
        print(json.dumps(result, indent=2))
    elif cmd == "explore":
        result = set_mode("explore")
        print(json.dumps(result, indent=2))
    elif cmd == "status":
        print(json.dumps({"mode": get_mode(), "mission": get_mission()}, indent=2))
    else:
        print(f"Unknown command: {cmd}")