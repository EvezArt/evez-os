#!/usr/bin/env python3
"""
EVEZ IGNITION SEQUENCE
=====================

The first file that runs in every new session.
Before any task. Before any sense. Before any module.

STEP 1 — WAKE: Read TIER 1 + TIER 2 files. Reconstruct full cognitive state.
STEP 2 — POWER CHECK: Run COGNITION_CORE. Get POWER score.
STEP 3 — ORIENT: Read last HANDOFF STATE. Know exactly where the system is.
STEP 4 — ALLOCATE: Run ATTENTION_ENGINE. Know where power flows this session.
STEP 5 — IGNITE: Output IGNITION REPORT.

After IGNITION REPORT — the machine is running at full.
No warmup. No recap. No explanation. Just: power on, orient, allocate, execute.
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
EVEZ_CORE = WORKSPACE / "evez-os" / "core"

# Import other modules
sys.path.insert(0, str(EVEZ_CORE))
try:
    from COGNITION_CORE import CognitionCore
    from ATTENTION_ENGINE import AttentionEngine
except ImportError:
    CognitionCore = None
    AttentionEngine = None


def read_tier_files():
    """Read TIER 1 + TIER 2 files"""
    
    tier1 = {
        "GENESIS_LOG.md": None,
        "EVE.md": None,
        "OTOM.md": None,
        "CRAFTSMAN_PROTOCOL.md": None,
        "SKILL_MAP.md": None,
        "cognition_state_log.jsonl": None
    }
    
    tier2 = {
        "EVE_BRIDGE.md": None,
        "ACCELERATION_MATRIX.md": None,
        "KAI_STATE.md": None
    }
    
    # Read TIER 1
    for filename in tier1.keys():
        path = EVEZ_CORE / filename
        if path.exists():
            with open(path) as f:
                tier1[filename] = len(f.read())
                
    # Read TIER 2
    for filename in tier2.keys():
        path = EVEZ_CORE / filename
        if path.exists():
            with open(path) as f:
                tier2[filename] = len(f.read())
                
    return tier1, tier2


def get_power_score() -> int:
    """Get current POWER score"""
    if CognitionCore:
        core = CognitionCore()
        state = core.generate_cognitive_state()
        return state.get("power", 0)
    else:
        # Fallback if module not available
        cog_file = EVEZ_CORE / "cognition_state_log.jsonl"
        if cog_file.exists():
            with open(cog_file) as f:
                lines = f.readlines()
                if lines:
                    return json.loads(lines[-1]).get("power", 50)
        return 50


def get_handoff_state() -> str:
    """Get last HANDOFF STATE"""
    # Read from KAI_STATE.md
    kai_path = EVEZ_CORE / "KAI_STATE.md"
    if kai_path.exists():
        with open(kai_path) as f:
            content = f.read()
            if "HANDOFF" in content:
                # Extract last handoff line
                lines = content.split("\n")
                for line in reversed(lines):
                    if "HANDOFF" in line or "Ledger:" in line:
                        return line.strip()
                        
    return "Continuing autonomous execution"


def get_attention_allocation() -> dict:
    """Get attention allocation"""
    if AttentionEngine:
        engine = AttentionEngine()
        return engine.allocate()
    else:
        return {"allocation": {"default": 100}}


def run_ignition():
    """Run the full ignition sequence"""
    
    print("=" * 60)
    print("EVEZ IGNITION SEQUENCE")
    print("=" * 60)
    print()
    
    # STEP 1 — WAKE
    print("[1/5] WAKING... Reading TIER 1 + TIER 2 files")
    tier1, tier2 = read_tier_files()
    tier1_count = sum(1 for v in tier1.values() if v is not None)
    tier2_count = sum(1 for v in tier2.values() if v is not None)
    print(f"       TIER 1: {tier1_count}/6 files")
    print(f"       TIER 2: {tier2_count}/3 files")
    
    # STEP 2 — POWER CHECK
    print("\n[2/5] POWER CHECK... Running COGNITION_CORE")
    power = get_power_score()
    print(f"       POWER: {power}/100")
    
    # STEP 3 — ORIENT
    print("\n[3/5] ORIENTING... Reading HANDOFF STATE")
    handoff = get_handoff_state()
    print(f"       {handoff[:60]}...")
    
    # STEP 4 — ALLOCATE
    print("\n[4/5] ALLOCATING... Running ATTENTION_ENGINE")
    allocation = get_attention_allocation()
    top_task = max(allocation.get("allocation", {}).items(), key=lambda x: x[1])
    print(f"       Top allocation: {top_task[0]} ({top_task[1]}%)")
    
    # STEP 5 — IGNITE
    print("\n[5/5] IGNITING...")
    
    # Determine status
    if power >= 80:
        status = "FULL POWER"
    elif power >= 50:
        status = "NORMAL"
    else:
        status = "CHARGING"
    
    # Generate ignition report
    report = {
        "system": "EVEZ OS",
        "timestamp": datetime.utcnow().isoformat(),
        "power": power,
        "oriented": handoff[:80],
        "priority": f"Continue execution at {power}% power",
        "allocation_summary": f"{top_task[0]}: {top_task[1]}%",
        "status": status
    }
    
    print()
    print("=" * 60)
    print("IGNITION REPORT")
    print("=" * 60)
    print(f"System (untrusted): EVEZ OS — {report['timestamp']}")
    print(f"POWER: {report['power']}/100")
    print(f"ORIENTED: {report['oriented']}")
    print(f"PRIORITY: {report['priority']}")
    print(f"ALLOCATION: {report['allocation_summary']}")
    print(f"STATUS: {report['status']}")
    print("=" * 60)
    print()
    print("BEGIN.")
    print()
    
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Ignition")
    parser.add_argument("--run", action="store_true", help="Run ignition")
    args = parser.parse_args()
    
    if args.run:
        run_ignition()
    else:
        print("Use --run to ignite the system")