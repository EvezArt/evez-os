#!/usr/bin/env python3
"""
EVEZ Assets Launcher - Unified entry point for all EVEZ-style modules
Run: python3 launcher.py [command]
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    if len(sys.argv) < 2:
        print("=== EVEZ Assets Launcher ===")
        print("\nAvailable commands:")
        print("  spine         - Run event spine demo")
        print("  agent         - Run autonomous agent demo")
        print("  memory        - Run memory store demo")
        print("  cognition     - Run cognition engine demo")
        print("  loop          - Run autonomous loop demo")
        print("  swarm         - Run swarm orchestrator demo")
        print("  finance       - Run finance engine demo")
        print("  pattern       - Run pattern detector demo")
        print("  network       - Run network mesh demo")
        print("  meta          - Run meta-learner demo")
        print("  consciousness - Run consciousness demo")
        print("  integrator    - Run unified integrator (ALL SYSTEMS)")
        print("  full          - Run full integrated system demo")
        print("  api           - Start HTTP API server (port 8765)")
        print("\nUsage: python3 launcher.py [command]")
        print("\nUsage: python3 launcher.py [command]")
        return
    
    command = sys.argv[1].lower()
    
    if command == "spine":
        from spine import EventSpine
        spine = EventSpine("./demo_spine.jsonl")
        spine.append("TEST", {"message": "Hello EVEZ"})
        print(f"Spine state: {spine.get_state()}")
        
    elif command == "agent":
        from autonomous_agent import ContextualBanditAgent
        import random
        agent = ContextualBanditAgent("Demo")
        for i in range(10):
            d = agent.decide(random.uniform(15, 45), random.uniform(0.3, 1.2))
            print(f"Decision: {d.backend.value}")
        print(f"Stats: {agent.get_stats()}")
        
    elif command == "memory":
        from memory_store import UnifiedMemory
        memory = UnifiedMemory("./demo_memory.jsonl")
        memory.store("First memory", tags=["init"])
        memory.store("Second memory", tags=["test"])
        print(f"Search: {memory.search('first')}")
        
    elif command == "cognition":
        from cognition_engine import CognitionEngine
        engine = CognitionEngine()
        events = engine.simulate_thought(5)
        print(f"Topology: {engine.get_topology()}")
        
    elif command == "loop":
        from autonomous_loop import AutonomousLoop
        loop = AutonomousLoop()
        for i in range(5):
            result = loop.run_cycle()
            print(f"Cycle {i+1}: {result['orientation']['state']}")
        
    elif command == "swarm":
        from swarm_orchestrator import SwarmOrchestrator, TaskPriority
        swarm = SwarmOrchestrator("Demo")
        swarm.register_agent("a1", "Alpha", ["search"])
        swarm.register_agent("a2", "Beta", ["code"])
        swarm.submit_task("Test task", TaskPriority.HIGH)
        for i in range(3):
            print(f"Cycle {i+1}: {swarm.run_cycle()}")
        print(f"Status: {swarm.get_status()}")
        
    elif command == "finance":
        from finance_engine import FinanceEngine
        finance = FinanceEngine(10000)
        for i in range(10):
            result = finance.auto_trade_cycle()
        print(f"Performance: {finance.get_performance()}")
        
    elif command == "pattern":
        from pattern_detector import PatternDetector
        detector = PatternDetector()
        patterns = detector.detect_patterns(threshold=0.4)
        print(f"Patterns: {len(patterns)} detected")
        for p in detector.get_strongest_patterns(3):
            print(f"  {p.domain_a} ↔ {p.domain_b}: {p.correlation:.3f}")
        
    elif command == "network":
        from network_mesh import NetworkMesh
        network = NetworkMesh("main-node", 9000)
        network.discover_node("peer-1", "10.0.0.1", 9001, ["spine"])
        network.discover_node("peer-2", "10.0.0.2", 9002, ["cognition"])
        network.propose("prop-001", {"action": "test"})
        network.vote("prop-001")
        print(f"Topology: {network.get_topology()}")
        
    elif command == "meta":
        from meta_learner import MetaLearner
        import random
        learner = MetaLearner()
        contexts = [{"domain": "finance"}, {"domain": "cognition"}]
        for i in range(20):
            learner.record(random.choice(contexts), random.choice(["optimize", "expand"]), random.uniform(-1, 1))
        result = learner.meta_learn()
        print(f"Strategy: {result['current_strategy']}, Events: {result['total_learning_events']}")
        
    elif command == "consciousness":
        from consciousness import Consciousness
        consciousness = Consciousness()
        consciousness.experience("init", 0.9, "System initialized")
        consciousness.introspect("capabilities")
        thought = consciousness.think("self_improvement")
        print(f"Awareness: {thought['awareness_level']}, Confidence: {thought['self_model_confidence']:.2f}")
        print(f"State: {consciousness.get_state()['awareness_level']}")
        
    elif command == "integrator":
        from integrator import EVEZIntegrator
        integrator = EVEZIntegrator()
        for i in range(3):
            result = integrator.run_cycle()
            print(f"Cycle {result['cycle']}: {result['state']} → {result['decision']}")
        print(f"Status: {integrator.get_system_status()['subsystems']}")
        
    elif command == "full":
        print("=== Full EVEZ System Integration ===\n")
        
        # Initialize all components
        from spine import EventSpine
        from autonomous_agent import ContextualBanditAgent
        from memory_store import UnifiedMemory
        from cognition_engine import CognitionEngine
        from autonomous_loop import AutonomousLoop
        
        # Create integrated system
        spine = EventSpine("./full_spine.jsonl")
        agent = ContextualBanditAgent("Integrated")
        memory = UnifiedMemory("./full_memory.jsonl")
        cognition = CognitionEngine()
        loop = AutonomousLoop()
        
        # Run integrated cycle
        print("Running integrated autonomous cycle...")
        
        # Step 1: Observe
        obs = loop.observe()
        print(f"  [Observe] CPU: {obs['metrics']['cpu_usage']:.1f}%")
        
        # Step 2: Orient + decide
        orient = loop.orient(obs)
        decision = loop.decide(orient)
        print(f"  [Decide] {decision['action_type']} on {decision['target']}")
        
        # Step 3: Act + log to spine
        action = loop.act(decision)
        spine.append("ACTION", action)
        
        # Step 4: Store in memory
        memory.store(f"Executed {decision['action_type']}", tags=["action", decision['action_type']])
        
        # Step 5: Create cognition event
        cognition.F(
            f"Action {decision['action_type']} completed with result {action['result']}",
            evidence=[action['timestamp']],
            falsifiers=["action failed completely"],
            confidence=0.8
        )
        
        # Step 6: Reflect
        reflection = loop.reflect(action, orient)
        
        print("\n=== Integrated System Status ===")
        print(f"  Spine events: {len(spine.chain)}")
        print(f"  Agent decisions: {agent.get_stats()['total_decisions']}")
        print(f"  Memory entries: {memory.get_stats()['total_memories']}")
        print(f"  Cognition events: {len(cognition.events)}")
        print(f"  Loop cycles: {loop.cycle_count}")
        
    else:
        print(f"Unknown command: {command}")
        print("Run with no arguments to see available commands")

if __name__ == "__main__":
    main()