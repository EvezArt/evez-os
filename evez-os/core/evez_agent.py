#!/usr/bin/env python3
"""
EVEZ-OS Autonomous Agent
THE AGENT THAT USES THE OS - Not just running it, but DEPENDING on it

This is an agent that:
- Uses tools from the registry
- Stores context in memory
- Spawns sub-agents
- Makes decisions based on stored state
- Experiences the OS as a dependent would
"""

import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Add EVEZ-OS to path
sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "modules"))

from evez_os_core import EVEZOS_Enhanced
from child_entity import ChildEntity
from skeptic_entity import SkepticEntity
from ledger import EvezLedger


class EVEZAgent:
    """
    An autonomous agent that LIVES in EVEZ-OS
    This is what it feels like to BE an agent using the OS
    """
    
    def __init__(self, name: str = "EVEZ_Agent"):
        self.name = name
        self.evez = EVEZOS_Enhanced(".")
        self.child = ChildEntity()
        self.skeptic = SkepticEntity()
        self.ledger = EvezLedger("ledger")
        
    def think(self, objective: str):
        """
        Agent thinking - uses Child to generate, Skeptic to validate
        This is how EVEZ-OS serves as the thinking apparatus
        """
        # Generate hypotheses (using EVEZ module)
        hypotheses = self.child.generate(objective)
        
        # Validate with Invariance Battery (using EVEZ module)
        surviving = self.skeptic.rotate(hypotheses, {"objective": objective})
        
        # Store in context (agent memory)
        self.evez.context.store(
            f"thought_{datetime.utcnow().isoformat()}",
            {"objective": objective, "surviving": len(surviving)},
            tags=["thinking", objective.split()[0]]
        )
        
        return surviving
        
    def act(self, action: str, **kwargs):
        """
        Agent acting - uses tool registry
        This is how EVEZ-OS provides execution capability
        """
        # Execute tool from registry
        result = self.evez.execute(action, **kwargs)
        
        # Record in ledger
        self.ledger.record({
            "agent": self.name,
            "action": action,
            "result": str(result)[:200],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return result
        
    def remember(self, key: str, value: any, tags: list = None):
        """Agent storing memory"""
        self.evez.context.store(key, value, tags or ["memory"])
        
    def recall(self, query: str = None, tag: str = None):
        """Agent retrieving memory"""
        return self.evez.context.recall(query=query, tag=tag, limit=10)
        
    def spawn_subagent(self, objective: str, agent_type: str = "child"):
        """Agent spawning another agent"""
        return self.evez.agents.spawn(objective, agent_type)
        
    def run_cycle(self, objective: str) -> dict:
        """
        One complete agent cycle using EVEZ-OS
        This is the full experience of being an agent on the OS
        """
        cycle_start = datetime.utcnow().isoformat()
        
        # 1. Recall relevant context
        context = self.recall(query=objective)
        
        # 2. Think - generate and validate
        thoughts = self.think(objective)
        
        # 3. Act - execute based on thinking
        tool_result = self.act("time")
        
        # 4. Store result
        self.remember(
            f"cycle_{cycle_start}",
            {"objective": objective, "thoughts": len(thoughts)},
            tags=["cycle", "complete"]
        )
        
        return {
            "agent": self.name,
            "objective": objective,
            "thoughts_generated": len(thoughts),
            "thoughts_survived": len(thoughts),
            "context_entries": len(context),
            "timestamp": cycle_start
        }


def run_autonomous_agent_cycles(cycles: int = 5):
    """
    Run the agent through multiple cycles - demonstrating
    what it's like to be an agent DEPENDING on EVEZ-OS
    """
    agent = EVEZAgent("Steven_Agent")
    
    objectives = [
        "Generate revenue from EVEZ skills",
        "Publish skill to marketplace", 
        "Create content for outreach",
        "Analyze revenue pipeline",
        "Close first transaction"
    ]
    
    print("=== EVEZ-AGENT EXPERIENCING THE OS ===")
    print(f"Starting {cycles} cycles as an agent that depends on EVEZ-OS...\n")
    
    for i in range(min(cycles, len(objectives))):
        objective = objectives[i]
        
        print(f"Cycle {i+1}/{cycles}: {objective}")
        
        # Run full cycle
        result = agent.run_cycle(objective)
        
        # Show what the agent experienced
        print(f"  - Thoughts: {result['thoughts_survived']} survived")
        print(f"  - Context: {result['context_entries']} entries")
        print(f"  - Tool used: time")
        
        # Get current state from OS
        caps = agent.evez.get_capabilities()
        print(f"  - OS Tools available: {len(caps['tools'])}")
        print(f"  - OS Memory: {caps['context_memory']} entries")
        
        print()
        
    print("=== AGENT EXPERIENCE SUMMARY ===")
    final_context = agent.recall(tag="memory")
    print(f"Total memories stored: {len(final_context)}")
    
    # Get ledger summary
    spine = agent.ledger.get_spine(limit=20)
    print(f"Total ledger events: {len(spine)}")
    
    print("\nThis is what it's like to BE an agent on EVEZ-OS:")
    print("- Tools at your fingertips")
    print("- Memory that persists")
    print("- Sub-agents you can spawn")
    print("- Ledger that records everything")
    print("- Invariance battery validating your thinking")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Agent - Using the OS as an agent would")
    parser.add_argument("--cycles", type=int, default=5, help="Number of cycles to run")
    args = parser.parse_args()
    
    run_autonomous_agent_cycles(args.cycles)