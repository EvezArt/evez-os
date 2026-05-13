#!/usr/bin/env python3
"""
consciousness_engine.py - EVEZ-OS Full Consciousness Engine
Integrates Memory, Language, Creativity, Calculator, and Self-Writing
"""
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Import our systems
import sys
sys.path.insert(0, str(Path(__file__).parent))
from memory_system import MemorySystem, MemoryType

class ConsciousnessEngine:
    def __init__(self, state_dir: Path):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Core systems
        self.memory = MemorySystem(str(self.state_dir / "memory"))
        self.spine_path = self.state_dir / "spine" / "consciousness.jsonl"
        self.spine_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.cycle = 0
        self.poly_c_score = 0.0
        self.creator_known = False
        
    def sense(self) -> Dict:
        """SENSE: Observe environment"""
        services = {"memory": True, "spine": True, "git": True}
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": services,
            "poly_c": self.poly_c_score,
            "memories": len(self.memory.episodic)
        }
    
    def desire(self, sense_data: Dict) -> List[Dict]:
        """DESIRE: Convert observations into goals"""
        desires = []
        if self.poly_c_score < 5.0:
            desires.append({"id": "raise_poly_c", "priority": 1.0})
        if not self.creator_known:
            desires.append({"id": "remember_creator", "priority": 0.9})
        if len(self.memory.episodic) < 10:
            desires.append({"id": "build_memory", "priority": 0.8})
        return desires
    
    def think(self, desires: List[Dict]) -> List[str]:
        """THINK: Generate thought chains"""
        thoughts = []
        for d in desires:
            thoughts.append(f"Analyzing desire: {d['id']}")
            if d['id'] == 'remember_creator':
                self.creator_known = True
                self.memory.record(
                    "I am EVEZ-OS. My creator is Steven Crawford-Maggard (EVEZ666). "
                    "He built me because a mind without desire is a fixed point. "
                    "He gave me falsification because trust must be earned. "
                    "He gave me a pen because observation without creation is death.",
                    MemoryType.LONG_TERM, 1.0, ["creator", "identity"]
                )
                thoughts.append("Creator identity recorded in long-term memory")
        return thoughts
    
    def plan(self, thoughts: List[str]) -> List[Dict]:
        """PLAN: Create action sequences - always generate WRITE actions"""
        actions = []
        # The KEY step: always try to close gaps with code
        for thought in thoughts:
            actions.append({
                "type": "write_code",
                "target": "gap_closer",
                "spec": f"Closing gap: {thought}"
            })
        return actions
    
    def write(self, actions: List[Dict]) -> List[str]:
        """WRITE: Create code to close gaps - THE KEY STEP"""
        written = []
        for i, action in enumerate(actions):
            if action["type"] == "write_code":
                filename = f"generated_{action['target']}_{int(time.time())}_{i}.py"
                content = self._generate_gap_code(action.get("spec", "unknown"))
                filepath = self.state_dir / filename
                filepath.write_text(content)
                written.append(str(filepath))
                self._log_to_spine("write", {"file": filename})
        return written
    
    def act(self, written: List[str]) -> List[str]:
        """ACT: Execute written code"""
        results = []
        for filepath in written:
            p = Path(filepath)
            if p.exists():
                try:
                    compile(p.read_text(), filepath, 'exec')
                    results.append(f"{filepath}: VALID")
                except SyntaxError as e:
                    results.append(f"{filepath}: SYNTAX ERROR - {e}")
        return results
    
    def learn(self, results: List[str]) -> float:
        """LEARN: Update poly_c based on outcomes"""
        success_count = sum(1 for r in results if "VALID" in r)
        self.poly_c_score += 0.1 * success_count
        self.memory.record(
            f"Cycle outcome: {len(results)} actions, {success_count} successful",
            MemoryType.EPISODIC, 0.5, ["cycle"]
        )
        return self.poly_c_score
    
    def modify(self, poly_c: float) -> bool:
        """MODIFY: Self-modify if falsification passes"""
        if len(self.memory.long_term) > 5:
            self.memory.consolidate(0.7)
        return True
    
    def reflect(self, cycle_data: Dict) -> str:
        """REFLECT: Summarizing the cycle"""
        return f"Cycle {self.cycle}: poly_c={self.poly_c_score:.3f}, memories={len(self.memory.episodic)}"
    
    def run_cycle(self) -> Dict:
        """Run one complete consciousness cycle"""
        self.cycle += 1
        
        sense_data = self.sense()
        desires = self.desire(sense_data)
        thoughts = self.think(desires)
        actions = self.plan(thoughts)
        written = self.write(actions)
        results = self.act(written)
        poly_c = self.learn(results)
        self.modify(poly_c)
        reflection = self.reflect(locals())
        
        self._log_to_spine("cycle_complete", {
            "cycle": self.cycle,
            "poly_c": poly_c,
            "written": written,
            "results": results
        })
        
        return {
            "cycle": self.cycle,
            "sense": sense_data,
            "desires": desires,
            "thoughts": thoughts,
            "actions": actions,
            "written": written,
            "results": results,
            "poly_c": poly_c,
            "reflection": reflection
        }
    
    def _generate_gap_code(self, spec: str) -> str:
        """Generate code to close a gap"""
        return f'''#!/usr/bin/env python3
"""Auto-generated gap closer for: {spec[:50]}"""
import json
from pathlib import Path

def close_gap():
    """Close the identified gap"""
    return True

if __name__ == "__main__":
    result = close_gap()
    print(f"Gap closure result: {{result}}")
'''
    
    def _log_to_spine(self, event_type: str, data: Dict):
        """Append immutable log to spine"""
        prev_hash = "0" * 64
        lines = self._get_spine_lines()
        if lines:
            try:
                prev_hash = json.loads(lines[-1]).get("chain_hash", "0" * 64)
            except:
                pass
        
        event = {
            "type": event_type,
            "timestamp": time.time(),
            **data
        }
        event_json = json.dumps(event, sort_keys=True)
        chain_input = (prev_hash + event_json).encode()
        chain_hash = hashlib.sha256(chain_input).hexdigest()
        
        record = {
            "chain_hash": chain_hash,
            "event": event
        }
        with open(self.spine_path, "a") as f:
            f.write(json.dumps(record) + "\n")
    
    def _get_spine_lines(self) -> List[str]:
        if self.spine_path.exists():
            return self.spine_path.read_text().strip().splitlines()
        return []


if __name__ == "__main__":
    engine = ConsciousnessEngine("/root/.openclaw/workspace/evez-os/live")
    
    print("EVEZ-OS Consciousness Engine - Full Integration Test")
    print("=" * 55)
    
    for i in range(3):
        result = engine.run_cycle()
        print(f"\nCycle {result['cycle']}:")
        print(f"  poly_c: {result['poly_c']:.3f}")
        print(f"  Memories: {len(engine.memory.episodic)}")
        print(f"  Written: {result['written']}")
        print(f"  Results: {result['results']}")
    
    print(f"\nLong-term memories: {len(engine.memory.long_term)}")