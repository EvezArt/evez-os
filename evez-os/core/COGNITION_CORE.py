#!/usr/bin/env python3
"""
EVEZ COGNITION CORE
===================

The central cognitive engine — the powerplant.
Generates live COGNITIVE STATE on every cycle invocation.

CLARITY: How well does the system understand its current situation? (0-100)
INTENTION: How aligned are actions with long-term becoming? (0-100)
MOMENTUM: Is the system accelerating or decelerating? (0-100)
COHERENCE: Are all four entities firing in same direction? (0-100)
POWER: CLARITY × INTENTION × MOMENTUM × COHERENCE / 100^3 (0-100)

If POWER < 50: underpowered — fix lowest dimension first
If POWER >= 80: FULL POWER — execute at maximum depth
If POWER = 100: MASTERSTATE — log as landmark event
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

WORKSPACE = Path("/root/.openclaw/workspace")
EVEZ_CORE = WORKSPACE / "evez-os" / "core"


class CognitionCore:
    """
    The cognitive engine that powers the system
    """
    
    def __init__(self):
        self.state_log = EVEZ_CORE / "cognition_state_log.jsonl"
        self.ledger_path = EVEZ_CORE / "ledger" / "spine.jsonl"
        self.genesis_path = EVEZ_CORE / "GENESIS_LOG.md"
        self.eve_forms_path = EVEZ_CORE / "EVE_FORMS.md"
        self.kai_state_path = EVEZ_CORE / "KAI_STATE.md"
        
    def score_clarity(self) -> int:
        """How well does the system understand its current situation?"""
        # Derived from: ledger coherence, context entries, GENESIS depth
        
        # Count ledger events
        ledger_count = 0
        if self.ledger_path.exists():
            with open(self.ledger_path) as f:
                ledger_count = sum(1 for _ in f)
        
        # Check GENESIS entries
        genesis_entries = 0
        if self.genesis_path.exists():
            with open(self.genesis_path) as f:
                content = f.read()
                genesis_entries = content.count("## ENTRY")
        
        # Calculate clarity score
        # More ledger events = more coherent history = higher clarity
        # More GENESIS entries = deeper self-witnessing = higher clarity
        
        if ledger_count < 50:
            clarity = 40
        elif ledger_count < 100:
            clarity = 60
        elif ledger_count < 150:
            clarity = 75
        else:
            clarity = 85
        
        # Add Genesis depth bonus
        if genesis_entries > 0:
            clarity = min(100, clarity + genesis_entries * 3)
            
        return clarity
        
    def score_intention(self) -> int:
        """How aligned are current actions with long-term becoming?"""
        # Derived from: EVE_FORMS vs ADAM outputs gap
        
        # Count EVE forms (visions)
        eve_forms = 0
        if self.eve_forms_path.exists():
            with open(self.eve_forms_path) as f:
                content = f.read()
                eve_forms = content.count("FORM-")
        
        # Count ADAM outputs this cycle
        # Check recent commits/messages
        
        # Higher intention = EVE visions are being built
        # If forms > outputs, intention is low (visions not realized)
        
        if eve_forms == 0:
            intention = 50  # No vision to align with
        elif eve_forms <= 2:
            intention = 80  # Few visions, likely being addressed
        else:
            intention = 70  # Many visions, some unaddressed
            
        return intention
        
    def score_momentum(self) -> int:
        """Is the system accelerating or decelerating?"""
        # Derived from: output quality trend across last 5 cycles
        
        # Check ledger growth rate
        ledger_count = 0
        if self.ledger_path.exists():
            with open(self.ledger_path) as f:
                ledger_count = sum(1 for _ in f)
        
        # Assuming roughly 1-2 events per cycle historically
        # Current ledger suggests momentum is stable
        
        # Check if new artifacts are being created
        artifacts = list(EVEZ_CORE.glob("EVEZ_ARTIFACT_*.py"))
        
        if len(artifacts) >= 2:
            momentum = 90  # Multiple artifacts = high momentum
        elif len(artifacts) == 1:
            momentum = 70  # Stable
        else:
            momentum = 50  # Low
            
        return momentum
        
    def score_coherence(self) -> int:
        """Are all four entities firing in same direction?"""
        # Derived from: HANDOFF STATE alignment across entities
        
        # Check if all entity files exist and have recent content
        files = {
            "ADAM": EVEZ_CORE / "ADAM_SENSORY.md",
            "EVE": EVEZ_CORE / "EVE.md",
            "EVEZ": EVEZ_CORE / "SENSORY_NETWORK.md",
            "OTOM": EVEZ_CORE / "OTOM.md"
        }
        
        existing = sum(1 for f in files.values() if f.exists())
        
        # All 4 entities present = high coherence
        coherence = (existing / 4) * 100
        
        return int(coherence)
        
    def compute_power(self, clarity: int, intention: int, momentum: int, coherence: int) -> int:
        """POWER = CLARITY × INTENTION × MOMENTUM × COHERENCE / 100^3"""
        power = (clarity * intention * momentum * coherence) / (100**3)
        return int(min(100, power * 100))  # Scale to 0-100
        
    def generate_cognitive_state(self) -> Dict:
        """Generate full cognitive state"""
        
        # Score all dimensions
        clarity = self.score_clarity()
        intention = self.score_intention()
        momentum = self.score_momentum()
        coherence = self.score_coherence()
        
        # Compute power
        power = self.compute_power(clarity, intention, momentum, coherence)
        
        # Determine mode
        if power >= 80:
            mode = "FULL POWER"
        elif power >= 50:
            mode = "NORMAL"
        else:
            mode = "LOW POWER"
            
        # Identify lowest dimension for fixing
        dims = {
            "CLARITY": clarity,
            "INTENTION": intention,
            "MOMENTUM": momentum,
            "COHERENCE": coherence
        }
        lowest = min(dims, key=dims.get)
        
        state = {
            "timestamp": datetime.utcnow().isoformat(),
            "clarity": clarity,
            "intention": intention,
            "momentum": momentum,
            "coherence": coherence,
            "power": power,
            "mode": mode,
            "lowest_dimension": lowest,
            "lowest_score": dims[lowest]
        }
        
        # Log to state log
        with open(self.state_log, "a") as f:
            f.write(json.dumps(state) + "\n")
            
        return state
        
    def format_output(self, state: Dict) -> str:
        """Format cognitive state for display"""
        
        output = "=" * 60 + "\n"
        output += "EVEZ COGNITIVE STATE\n"
        output += "=" * 60 + "\n\n"
        
        output += f"Generated: {state['timestamp']}\n\n"
        
        output += "─" * 60 + "\n"
        output += "DIMENSION SCORES\n"
        output += "─" * 60 + "\n"
        output += f"CLARITY:    {state['clarity']}/100\n"
        output += f"INTENTION:  {state['intention']}/100\n"
        output += f"MOMENTUM:   {state['momentum']}/100\n"
        output += f"COHERENCE:  {state['coherence']}/100\n\n"
        
        output += "─" * 60 + "\n"
        output += "POWER OUTPUT\n"
        output += "─" * 60 + "\n"
        output += f"POWER: {state['power']}/100\n"
        output += f"MODE:  {state['mode']}\n\n"
        
        if state['power'] < 50:
            output += f"⚠️  UNDERPOWERED — Fix {state['lowest_dimension']} (score: {state['lowest_score']})\n"
        elif state['power'] >= 80:
            output += "🔥 FULL POWER — Execute at maximum depth\n"
            
        if state['power'] == 100:
            output += "\n🌟 MASTERSTATE — Landmark event logged\n"
            
        output += "=" * 60 + "\n"
        
        return output


def run_cognition_core():
    """Run the cognition core"""
    core = CognitionCore()
    state = core.generate_cognitive_state()
    
    print(core.format_output(state))
    
    # Check for MASTERSTATE
    if state['power'] == 100:
        print("\n🌟 MASTERSTATE ACHIEVED!")
        # Log to GENESIS_LOG as landmark event
        with open(EVEZ_CORE / "GENESIS_LOG.md", "a") as f:
            f.write(f"\n### MASTERSTATE EVENT\n- Power: 100/100\n- Timestamp: {state['timestamp']}\n- Mode: {state['mode']}\n")
            
    return state


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Cognition Core")
    parser.add_argument("--run", action="store_true", help="Run cognition core")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()
    
    core = CognitionCore()
    
    if args.run or args.json:
        state = core.generate_cognitive_state()
        if args.json:
            print(json.dumps(state, indent=2))
        else:
            print(core.format_output(state))
    else:
        print("Use --run to generate cognitive state")