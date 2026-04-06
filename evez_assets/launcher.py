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
        print("\nCore Systems:")
        print("  integrator    - Run unified integrator (ALL SYSTEMS)")
        
        print("\nSensory Skills:")
        print("  vision        - Computer vision & image analysis")
        print("  audio         - Speech recognition & TTS")
        print("  robotics      - Motor control & sensors")
        
        print("\nCognitive Skills:")
        print("  nlp           - Natural language understanding")
        print("  cognition     - FIRE events with topology")
        print("  consciousness - Self-awareness & introspection")
        
        print("\nOperational Skills:")
        print("  spine         - Append-only event spine")
        print("  agent         - Autonomous decision agent")
        print("  memory        - Unified memory store")
        print("  loop          - OODA self-improvement loop")
        print("  meta          - Learning to learn")
        
        print("\nNetwork & Data:")
        print("  swarm         - Multi-agent orchestration")
        print("  network       - P2P mesh & consensus")
        print("  pattern       - Cross-domain pattern detection")
        print("  finance       - Trading & portfolio")
        
        print("\nInfrastructure:")
        print("  security      - Encryption & threat detection")
        print("  api           - HTTP API server (port 8765)")
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
        
    elif command == "vision":
        from vision import VisionEngine
        vision = VisionEngine()
        result = vision.analyze_image()
        print(f"Objects: {len(result['objects'])}, Scene: {result['scene_type']}")
        print(f"Text: {vision.detect_text()}")
        
    elif command == "audio":
        from audio import AudioEngine
        audio = AudioEngine()
        result = audio.listen()
        print(f"Heard: {result['transcription']}")
        print(f"Speak: {audio.speak('Acknowledged')}")
        
    elif command == "robotics":
        from robotics import RoboticsEngine
        robotics = RoboticsEngine()
        result = robotics.move_to(5.0, 3.0)
        print(f"Move: {result['status']}, Distance: {result['distance']:.2f}m")
        sensors = robotics.read_sensors()
        print(f"Sensors: {len(sensors['sensors'])} active")
        
    elif command == "nlp":
        from nlp import NLPEngine
        nlp = NLPEngine()
        result = nlp.parse("EVEZ system at location San Francisco is running great")
        print(f"Intent: {result['intent']['name']}, Sentiment: {result['sentiment']}")
        print(f"Entities: {len(result['entities'])}")
        
    elif command == "security":
        from security import SecurityEngine
        security = SecurityEngine()
        hashed = security.hash_data("test data")
        enc = security.encrypt("secret", "key1")
        threat = security.detect_threat({})
        print(f"Hash: {hashed[:16]}..., Threat: {threat['threat_level']}")
        
    elif command == "database":
        from database import DatabaseEngine, Column, DataType
        db = DatabaseEngine()
        db.create_table("test", [Column("id", DataType.INTEGER, True), Column("val", DataType.TEXT)])
        db.insert("test", {"id": 1, "val": "hello"})
        print(f"Tables: {len(db.tables)}, Rows: {db.select('test')}")
        
    elif command == "scheduler":
        from scheduler import SchedulerEngine
        scheduler = SchedulerEngine()
        scheduler.schedule_recurring("task1", 60, {"data": "test"})
        pending = scheduler.get_pending()
        print(f"Jobs: {len(scheduler.jobs)}, Pending: {len(pending)}")
        
    elif command == "cache":
        from cache import CacheEngine
        cache = CacheEngine(default_ttl=60)
        cache.set("x", 100)
        cache.set("y", {"nested": True})
        print(f"Get x: {cache.get('x')}, Stats: {cache.get_stats()}")
        
    elif command == "blockchain":
        from blockchain import BlockchainEngine, TransactionType
        bc = BlockchainEngine()
        bc.add_validator("alice", 500)
        bc.create_transaction("system", "alice", 100)
        block = bc.mine_block("alice")
        print(f"Chain: {len(bc.chain)} blocks, Valid: {bc.verify_chain()}")
        
    elif command == "crypto":
        from crypto import CryptoEngine, CryptoAsset, OrderSide, OrderType
        c = CryptoEngine()
        c.get_quote(CryptoAsset.BTC)
        print(f"Quote BTC: ${c.prices[CryptoAsset.BTC]:.2f}, Portfolio: ${c.get_portfolio_value():.2f}")
        
    elif command == "workflow":
        from workflow import WorkflowEngine, WorkflowNode, NodeType
        wf = WorkflowEngine()
        nodes = [WorkflowNode("s", NodeType.START, "Start"), WorkflowNode("e", NodeType.END, "End")]
        nodes[0].next_nodes = ["e"]
        wf.define_workflow("test", nodes)
        inst = wf.create_instance("test")
        print(f"Workflow: {len(wf.workflows)}, Instance: {inst}")
        
    elif command == "graph":
        from graph import GraphEngine
        g = GraphEngine()
        g.add_node("a", "Alpha"), g.add_node("b", "Beta"), g.add_edge("a", "b", "knows")
        path = g.bfs("a", "b")
        print(f"Graph: {len(g.nodes)} nodes, Path: {path}")
        
    elif command == "simulation":
        from simulation import SimulationEngine
        sim = SimulationEngine(20, 20)
        sim.add_particle(10, 10, 1, 1)
        sim.update_physics(5)
        print(f"Simulation: {len(sim.particles)} particles, Stats: {sim.get_particle_stats()}")
        
    elif command == "game":
        from game_theory import GameTheoryEngine, AgentStrategy, StrategyType
        gt = GameTheoryEngine()
        agents = [AgentStrategy("A", StrategyType.COOPERATE), AgentStrategy("B", StrategyType.DEFECT)]
        result = gt.simulate_tournament(agents, 10)
        print(f"Game: Winner: {result[0].name}, Score: {result[0].score}")
        
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