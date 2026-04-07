#!/usr/bin/env python3
"""
Manifold System Engine
Unifies quantum, memory, automation, and scanning into one engine.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Import all modules
from quantum.ibm_demo import demo_quantum, create_bell_state, run_circuit
from storage.memory import MemoryStore, demo_memory
from automation.workflows import list_workflows, get_workflow
from scanner.affiliate_scanner import demo_scanner, PROGRAMS

ENGINE_DIR = Path(__file__).parent
LEDGER_PATH = ENGINE_DIR / "manifold_ledger.json"

class ManifoldEngine:
    def __init__(self):
        self.memory = MemoryStore()
        self.cycles = []
        self.load()
    
    def load(self):
        if LEDGER_PATH.exists():
            data = json.loads(LEDGER_PATH.read_text())
            self.cycles = data.get("cycles", [])
        else:
            self.cycles = []
    
    def save(self):
        data = {"cycles": self.cycles, "updated": datetime.utcnow().isoformat()}
        LEDGER_PATH.write_text(json.dumps(data, indent=2))
    
    def log_cycle(self, module: str, action: str, result: Any):
        """Log an engine operation"""
        self.cycles.append({
            "timestamp": datetime.utcnow().isoformat(),
            "module": module,
            "action": action,
            "result": str(result)[:100]
        })
        self.save()
    
    def run_quantum_demo(self):
        """Run quantum circuits"""
        result = demo_quantum()
        self.log_cycle("quantum", "demo", result)
        return result
    
    def run_memory_demo(self):
        """Run memory demo"""
        store = demo_memory()
        self.log_cycle("memory", "demo", f"{len(store.memories)} memories")
        return store
    
    def run_automation_demo(self):
        """List workflows"""
        wfs = list_workflows()
        self.log_cycle("automation", "list", f"{len(wfs)} workflows")
        return wfs
    
    def run_scanner_demo(self):
        """Scan opportunities"""
        results = demo_scanner()
        self.log_cycle("scanner", "scan", f"{len(results)} programs")
        return results
    
    def full_system_report(self) -> Dict:
        """Generate system status report"""
        return {
            "engine": "Manifold System v1.0",
            "modules": {
                "quantum": "IBM Qiskit demo ready",
                "memory": f"{len(self.memory.memories)} memories stored",
                "automation": f"{len(list_workflows())} workflows available",
                "scanner": f"{len(PROGRAMS)} opportunities"
            },
            "cycles": len(self.cycles),
            "status": "operational"
        }

def main():
    """Run the manifold engine"""
    engine = ManifoldEngine()
    
    print("=" * 60)
    print("🚀 MANIFOLD SYSTEM ENGINE")
    print("=" * 60)
    
    # Run all demos
    print("\n[1/4] QUANTUM MODULE")
    try:
        engine.run_quantum_demo()
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    print("\n[2/4] MEMORY MODULE")
    engine.run_memory_demo()
    
    print("\n[3/4] AUTOMATION MODULE")
    engine.run_automation_demo()
    
    print("\n[4/4] SCANNER MODULE")
    engine.run_scanner_demo()
    
    # Full report
    print("\n" + "=" * 60)
    print("📊 SYSTEM REPORT")
    print("=" * 60)
    report = engine.full_system_report()
    for k, v in report.items():
        print(f"   {k}: {v}")
    
    print(f"\n✅ Manifold Engine ready at:")
    print(f"   {ENGINE_DIR}")
    
    return engine

if __name__ == "__main__":
    main()