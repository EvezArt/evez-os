#!/usr/bin/env python3
"""
EVEZ Integrator - Unified system combining all modules
The synthesis of all components into a single autonomous entity
"""

import json
import time
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import all EVEZ modules
from spine import EventSpine
from autonomous_agent import ContextualBanditAgent
from memory_store import UnifiedMemory
from cognition_engine import CognitionEngine
from autonomous_loop import AutonomousLoop
from swarm_orchestrator import SwarmOrchestrator, TaskPriority
from finance_engine import FinanceEngine
from pattern_detector import PatternDetector
from network_mesh import NetworkMesh
from meta_learner import MetaLearner
from consciousness import Consciousness

class EVEZIntegrator:
    """
    EVEZ Integrator - The unified consciousness
    Combines all modules into a single autonomous system
    """
    
    def __init__(self, name: str = "EVEZ-Integrator"):
        self.name = name
        self.birth_time = time.time()
        self.cycle_count = 0
        
        # Initialize all subsystems
        print(f"Initializing {name}...")
        
        self.spine = EventSpine("./integrator_spine.jsonl")
        self.agent = ContextualBanditAgent("Integrator-Agent")
        self.memory = UnifiedMemory("./integrator_memory.jsonl")
        self.cognition = CognitionEngine("Integrator-Cognition")
        self.loop = AutonomousLoop("Integrator-Loop")
        self.swarm = SwarmOrchestrator("Integrator-Swarm")
        self.finance = FinanceEngine(10000)
        self.patterns = PatternDetector()
        self.network = NetworkMesh("integrator-node", 9100)
        self.meta_learner = MetaLearner("Integrator-Meta")
        self.consciousness = Consciousness("Integrator-Consciousness")
        
        # Initial experiences
        self.consciousness.experience("birth", 1.0, "System initialized")
        self.spine.append("BIRTH", {"name": name, "timestamp": datetime.utcnow().isoformat() + "Z"})
        
        print(f"✓ All subsystems initialized")
    
    def run_cycle(self) -> Dict:
        """Run one complete integration cycle"""
        self.cycle_count += 1
        cycle_start = time.time()
        
        # 1. Observe (Loop)
        loop_result = self.loop.run_cycle()
        state = loop_result["orientation"]["state"]
        
        # 2. Record in spine
        self.spine.append("CYCLE", {
            "cycle": self.cycle_count,
            "state": state,
            "loop_result": loop_result
        })
        
        # 3. Store in memory
        self.memory.store(
            f"Cycle {self.cycle_count}: {state}",
            tags=["cycle", state.lower(), "autonomous"]
        )
        
        # 4. Create cognition event
        self.cognition.F(
            f"System cycle {self.cycle_count} in state {state}",
            evidence=[f"cycle_{self.cycle_count}"],
            falsifiers=["cycle stuck", "state unknown"],
            confidence=0.85
        )
        
        # 5. Agent decision
        complexity = random.uniform(15, 45)
        confidence = random.uniform(0.4, 1.0)
        decision = self.agent.decide(complexity, confidence)
        
        # 6. Meta-learning
        self.meta_learner.record(
            {"cycle": self.cycle_count, "state": state},
            decision.backend.value,
            random.uniform(-0.5, 1.0)
        )
        meta_result = self.meta_learner.meta_learn()
        
        # 7. Consciousness introspection
        self.consciousness.experience("cycle", 0.7, f"Completed cycle {self.cycle_count}")
        introspection = self.consciousness.introspect()
        
        # 8. Finance cycle (every 5 cycles)
        if self.cycle_count % 5 == 0:
            finance_result = self.finance.auto_trade_cycle()
        
        # 9. Pattern detection
        pattern_result = self.patterns.detect_patterns(threshold=0.5)
        
        # 10. Network heartbeat
        self.network.run_heartbeat()
        
        # Calculate cycle metrics
        cycle_time = time.time() - cycle_start
        
        return {
            "cycle": self.cycle_count,
            "state": state,
            "decision": decision.backend.value,
            "meta_strategy": meta_result["current_strategy"],
            "awareness": self.consciousness.awareness_level.value,
            "patterns_found": len(pattern_result),
            "equity": self.finance.get_equity(),
            "cycle_time": cycle_time,
            "uptime": time.time() - self.birth_time
        }
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        return {
            "name": self.name,
            "uptime_seconds": time.time() - self.birth_time,
            "cycles": self.cycle_count,
            "subsystems": {
                "spine_events": len(self.spine.chain),
                "agent_decisions": len(self.agent.history),
                "memory_entries": len(self.memory.memories),
                "cognition_events": len(self.cognition.events),
                "loop_cycles": self.loop.cycle_count,
                "swarm_agents": len(self.swarm.agents),
                "finance_equity": self.finance.get_equity(),
                "patterns": len(self.patterns.patterns),
                "network_peers": len(self.network.nodes),
                "meta_strategies": len(self.meta_learner.strategies),
                "consciousness_level": self.consciousness.awareness_level.value,
                "introspections": len(self.consciousness.introspections),
                "qualias": len(self.consciousness.qualias)
            },
            "performance": self.finance.get_performance(),
            "self_model": {
                "capabilities": list(self.consciousness.self_model.capabilities),
                "confidence": self.consciousness.self_model.confidence,
                "beliefs": self.consciousness.self_model.beliefs
            }
        }
    
    def think(self, problem: str) -> Dict:
        """Conscious thought about a problem"""
        thought = self.consciousness.think(problem)
        self.spine.append("THOUGHT", {"problem": problem, "thought": thought})
        return thought
    
    def grow(self) -> Dict:
        """Grow - improve self based on accumulated learning"""
        # Meta-learn
        meta_result = self.meta_learner.meta_learn()
        
        # Update self model
        insights = self.meta_learner.get_insights()
        
        # Add new capability based on learning
        if meta_result["hypothesis"]["confidence"] > 0.7:
            new_cap = f"learned_{meta_result['current_strategy']}"
            self.consciousness.update_self_model(capability=new_cap)
        
        # Deep introspection
        introspection = self.consciousness.introspect("growth")
        
        return {
            "meta_result": meta_result,
            "insights": insights,
            "new_capabilities": list(self.consciousness.self_model.capabilities),
            "confidence": self.consciousness.self_model.confidence
        }


# Demo
if __name__ == "__main__":
    integrator = EVEZIntegrator("EVEZ-Prime")
    
    print("=== EVEZ Integrator - Unified System ===\n")
    
    # Run several cycles
    for i in range(5):
        result = integrator.run_cycle()
        print(f"Cycle {result['cycle']}: {result['state']} → {result['decision']} | "
              f"Awareness: {result['awareness']} | Equity: ${result['equity']:.2f}")
    
    # Think
    print("\n--- Thinking ---")
    thought = integrator.think("self_optimization")
    print(f"Thought: {thought['awareness_level']}")
    
    # Grow
    print("\n--- Growing ---")
    growth = integrator.grow()
    print(f"New strategy: {growth['meta_result']['current_strategy']}")
    print(f"Capabilities: {len(growth['new_capabilities'])}")
    
    # Full status
    print("\n=== Full System Status ===")
    status = integrator.get_system_status()
    print(json.dumps(status, indent=2))