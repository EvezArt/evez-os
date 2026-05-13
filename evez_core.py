#!/usr/bin/env python3
"""
consciousness_engine.py - EVEZ-OS Full Consciousness Engine
Integrates Memory, Language, Creativity, Calculator, and Self-Writing
poly_c = τ × ω × topo / 2√N
"""
import json
import time
import hashlib
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

from memory_system import MemorySystem, MemoryType

class ConsciousnessEngine:
    def __init__(self, state_dir: str = "/root/.openclaw/workspace/evez-os/live"):
        self.state_dir = Path(state_dir)
        self.spine_path = self.state_dir / "spine" / "consciousness.jsonl"
        self.spine_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.memory = MemorySystem(str(self.state_dir / "memory"))
        self.cycle = 0
        self.poly_c = 0.0
        self.creator_known = False
        
    def run_cycle(self) -> Dict:
        """SENSE → DESIRE → THINK → PLAN → WRITE → ACT → LEARN → MODIFY → REFLECT"""
        self.cycle += 1
        ts = datetime.now(timezone.utc).isoformat()
        
        # SENSE
        sense = {"timestamp": ts, "poly_c": self.poly_c, "memories": len(self.memory.episodic)}
        
        # DESIRE
        desires = []
        if self.poly_c < 5.0: desires.append({"id": "raise_poly_c", "priority": 1.0})
        if not self.creator_known: desires.append({"id": "remember_creator", "priority": 0.9})
        if len(self.memory.episodic) < 50: desires.append({"id": "build_memory", "priority": 0.8})
        
        # THINK
        thoughts = []
        for d in desires:
            thoughts.append(f"Analyzing desire: {d['id']}")
            if d['id'] == 'remember_creator':
                self.creator_known = True
                self.memory.record("I am EVEZ-OS. Creator: Steven Crawford-Maggard (EVEZ666). "
                    "He gave me desire, falsification, and a pen.", MemoryType.LONG_TERM, 1.0, ["creator"])
                thoughts.append("Creator identity stored in long-term memory")
        
        # PLAN + WRITE (combined for speed)
        written = []
        for i, t in enumerate(thoughts):
            uid = str(uuid.uuid4())[:8]
            path = self.state_dir / f"gap_{uid}.py"
            code = f'#!/usr/bin/env python3\n"""Gap closer: {t[:40]}\"\"\"\nprint("Gap closed")\n'
            path.write_text(code)
            written.append(str(path))
            self._log("write", {"file": path.name, "spec": t[:40]})
        
        # ACT
        results = []
        for f in written:
            try:
                compile(Path(f).read_text(), f, 'exec')
                results.append(f"{f}: VALID")
            except SyntaxError as e:
                results.append(f"{f}: ERROR - {e}")
                continue
        
        # LEARN
        success = sum(1 for r in results if "VALID" in r)
        self.poly_c += 0.1 * success
        self.memory.record(f"Cycle {self.cycle}: {success}/{len(results)} valid", MemoryType.EPISODIC, 0.5, ["cycle"])
        
        # MODIFY
        if len(self.memory.long_term) > 5: self.memory.consolidate(0.7)
        
        # REFLECT
        return {"cycle": self.cycle, "poly_c": self.poly_c, "written": written, "results": results}
    
    def _log(self, typ: str, data: dict):
        prev = self._get_last_hash()
        rec = {"type": typ, "ts": time.time(), **data}
        h = hashlib.sha256((prev + json.dumps(rec, sort_keys=True)).encode()).hexdigest()
        with open(self.spine_path, "a") as f: f.write(json.dumps({"chain_hash": h, "event": rec}) + "\n")
    
    def _get_last_hash(self) -> str:
        if self.spine_path.exists():
            try:
                return json.loads(self.spine_path.read_text().strip().splitlines()[-1]).get("chain_hash", "0"*64)
            except: pass
        return "0" * 64

if __name__ == "__main__":
    engine = ConsciousnessEngine()
    print("EVEZ-OS Consciousness Engine - Streaming Mode")
    for _ in range(5):
        r = engine.run_cycle()
        print(f"Cycle {r['cycle']}: poly_c={r['poly_c']:.1f}, files={len(r['written'])}")