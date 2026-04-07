"""
EVEZ-OS Trunk Manager
Canonical state management with branch decomposition
"""

import json
from pathlib import Path
from datetime import datetime

class TrunkManager:
    def __init__(self, trunk_path):
        self.trunk_path = Path(trunk_path)
        self.trunk_path.mkdir(parents=True, exist_ok=True)
        self.state_file = self.trunk_path / "state.json"
        
    def initialize(self):
        """Initialize trunk state"""
        initial_state = {
            "objective": "Build EVEZ-OS",
            "last_completed": 0,
            "execution_gap": "Full system initialization",
            "next_action": "Run first harvest",
            "drift_risk": False,
            "branches": [],
            "history": [],
            "initialized": datetime.utcnow().isoformat()
        }
        self._save_state(initial_state)
        
    def get_state(self):
        """Load current trunk state"""
        if not self.state_file.exists():
            self.initialize()
        with open(self.state_file) as f:
            return json.load(f)
            
    def _save_state(self, state):
        """Save trunk state"""
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)
            
    def update(self, delta):
        """Update trunk state with delta"""
        state = self.get_state()
        state.update(delta)
        state["last_update"] = datetime.utcnow().isoformat()
        self._save_state(state)
        
    def decompose(self, objective):
        """Decompose objective into branches per the Arsenal"""
        # Standard decomposition sequence
        branches = [
            {
                "id": "recon",
                "role": "recon",
                "objective": f"Gather evidence for: {objective}",
                "tool": "perplexity"
            },
            {
                "id": "skeptic",
                "role": "skeptic",
                "objective": f"Stress-test the proposal: {objective}",
                "tool": "chatgpt"
            },
            {
                "id": "architect",
                "role": "architect",
                "objective": f"Refactor the surviving structure: {objective}",
                "tool": "claude"
            },
            {
                "id": "executor",
                "role": "executor",
                "objective": f"Route work for: {objective}",
                "tool": "base44"
            }
        ]
        
        # Update state with branches
        state = self.get_state()
        state["branches"] = branches
        state["objective"] = objective
        self._save_state(state)
        
        return branches
        
    def compress(self, results):
        """Compress branch results into canonical trunk state"""
        state = self.get_state()
        
        # Extract surviving logic from all results
        surviving = []
        for r in results:
            if r.get("status") == "success":
                surviving.append(r.get("output", {}))
                
        # Update state
        state["last_compression"] = datetime.utcnow().isoformat()
        state["surviving_logic"] = surviving
        state["history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "results": len(results),
            "surviving": len(surviving)
        })
        
        self._save_state(state)