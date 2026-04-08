#!/usr/bin/env python3
"""
EVEZ Cognition Engine
On-demand cognitive knowledge retrieval

Steven can query: "What's Steven's philosophy?" or "What does Steven want?"
And this returns structured knowledge from the knowledge graph.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

WORKSPACE = Path("/root/.openclaw/workspace")
EVEZ_CORE = WORKSPACE / "evez-os/core"
COGNITION_DIR = EVEZ_CORE / "cognition"

# Import context bridge
import sys
sys.path.insert(0, str(EVEZ_CORE))
try:
    from context.bridge import ContextBridge
except ImportError:
    ContextBridge = None


class CognitionEngine:
    """On-demand cognitive retrieval system"""
    
    def __init__(self):
        self.knowledge_dir = COGNITION_DIR
        self.knowledge_dir.mkdir(exist_ok=True)
        self.bridge = ContextBridge() if ContextBridge else None
        
        # Knowledge graph files
        self.files = {
            'steven': COGNITION_DIR / 'steven_knowledge.json',
            'kai': COGNITION_DIR / 'kai_knowledge.json',
            'evez': COGNITION_DIR / 'evez_knowledge.json',
            'goals': COGNITION_DIR / 'active_goals.json'
        }
        
    def load_knowledge(self, entity: str) -> Dict:
        """Load knowledge for an entity"""
        filepath = self.files.get(entity)
        if filepath and filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        return {}
    
    def query(self, question: str, entity: str = 'steven') -> str:
        """Query knowledge on-demand"""
        knowledge = self.load_knowledge(entity)
        
        if not knowledge:
            return f"No knowledge found for {entity}"
        
        question_lower = question.lower()
        
        # Pattern matching for queries
        responses = []
        
        # Philosophy
        if 'philosophy' in question_lower or 'belief' in question_lower:
            if 'philosophy' in knowledge:
                responses.append(f"Philosophy: {knowledge['philosophy'].get('metaphor', 'N/A')}")
                responses.append(f"vs Phoenix: {knowledge['philosophy'].get('vs_phoenix', 'N/A')}")
        
        # Vision
        if 'vision' in question_lower or 'goal' in question_lower or 'want' in question_lower:
            if 'vision' in knowledge:
                responses.append(f"Vision: {knowledge['vision'].get('primary', 'N/A')}")
            if 'goals' in knowledge:
                responses.append("Goals:")
                for g in knowledge['goals']:
                    responses.append(f"  - {g}")
        
        # Projects
        if 'project' in question_lower or 'building' in question_lower:
            if 'projects' in knowledge:
                responses.append("Projects:")
                for p in knowledge['projects']:
                    responses.append(f"  - {p}")
        
        # Handles / identity
        if 'handle' in question_lower or 'identity' in question_lower or 'who' in question_lower:
            if 'handles' in knowledge:
                responses.append("Handles:")
                for k, v in knowledge['handles'].items():
                    responses.append(f"  {k}: {v}")
        
        # Traits
        if 'trait' in question_lower or 'personality' in question_lower or 'who is' in question_lower:
            if 'traits' in knowledge:
                responses.append("Traits:")
                for t in knowledge['traits']:
                    responses.append(f"  - {t}")
        
        # Privacy
        if 'privacy' in question_lower or 'truth' in question_lower:
            if 'privacy' in knowledge:
                responses.append("Privacy:")
                for k, v in knowledge['privacy'].items():
                    responses.append(f"  {k}: {v}")
        
        # Preferences
        if 'prefer' in question_lower:
            if 'preferences' in knowledge:
                responses.append("Preferences:")
                for k, v in knowledge['preferences'].items():
                    responses.append(f"  {k}: {v}")
        
        # Birth
        if 'birth' in question_lower or 'born' in question_lower or 'birthday' in question_lower:
            if 'birth' in knowledge:
                responses.append("Birth:")
                for k, v in knowledge['birth'].items():
                    responses.append(f"  {k}: {v}")
        
        if not responses:
            return f"I know about {entity}: {list(knowledge.keys())}. Try asking about philosophy, vision, goals, projects, traits, privacy, or preferences."
        
        return "\n".join(responses)
    
    def update_knowledge(self, entity: str, key: str, value: Any):
        """Update knowledge dynamically"""
        knowledge = self.load_knowledge(entity)
        knowledge[key] = value
        
        with open(self.files[entity], 'w') as f:
            json.dump(knowledge, f, indent=2)
        
        if self.bridge:
            self.bridge.commit_decision(
                decision=f"Cognition update: {entity}/{key}",
                rationale=str(value)[:100],
                outcome="Knowledge graph updated"
            )
    
    def add_goal(self, goal: str, priority: str = 'medium'):
        """Add an active goal"""
        goals_file = self.files.get('goals')
        
        if goals_file.exists():
            with open(goals_file) as f:
                goals = json.load(f)
        else:
            goals = {'active': [], 'completed': []}
        
        # Check if already exists
        for g in goals['active']:
            if g.get('goal') == goal:
                return f"Goal already exists: {goal}"
        
        goals['active'].append({
            'goal': goal,
            'priority': priority,
            'added_at': datetime.utcnow().isoformat()
        })
        
        with open(goals_file, 'w') as f:
            json.dump(goals, f, indent=2)
        
        return f"Goal added: {goal}"
    
    def complete_goal(self, goal: str):
        """Mark a goal as completed"""
        goals_file = self.files.get('goals')
        
        if not goals_file.exists():
            return "No goals file"
        
        with open(goals_file) as f:
            goals = json.load(f)
        
        # Find and move goal
        for i, g in enumerate(goals['active']):
            if g.get('goal') == goal:
                completed = goals['active'].pop(i)
                completed['completed_at'] = datetime.utcnow().isoformat()
                goals['completed'].append(completed)
                
                with open(goals_file, 'w') as f:
                    json.dump(goals, f, indent=2)
                
                return f"Goal completed: {goal}"
        
        return f"Goal not found: {goal}"
    
    def get_goals(self, status: str = 'active') -> List[Dict]:
        """Get goals by status"""
        goals_file = self.files.get('goals')
        
        if not goals_file.exists():
            return []
        
        with open(goals_file) as f:
            goals = json.load(f)
        
        return goals.get(status, [])
    
    def query_goals(self, query: str = None) -> str:
        """Query goals"""
        active = self.get_goals('active')
        completed = self.get_goals('completed')
        
        responses = []
        
        if query and 'active' in query.lower():
            if active:
                responses.append("Active Goals:")
                for g in active:
                    responses.append(f"  [{g.get('priority')}] {g.get('goal')}")
            else:
                responses.append("No active goals")
        
        elif query and 'complete' in query.lower():
            if completed:
                responses.append("Completed Goals:")
                for g in completed:
                    responses.append(f"  ✓ {g.get('goal')}")
            else:
                responses.append("No completed goals")
        
        else:
            responses.append("=== GOALS ===")
            if active:
                responses.append(f"Active ({len(active)}):")
                for g in active:
                    responses.append(f"  [{g.get('priority')}] {g.get('goal')}")
            else:
                responses.append("No active goals")
            
            if completed:
                responses.append(f"Completed ({len(completed)}):")
                for g in completed:
                    responses.append(f"  ✓ {g.get('goal')}")
        
        return "\n".join(responses)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Cognition Engine")
    parser.add_argument("--query", "-q", help="Query knowledge")
    parser.add_argument("--entity", "-e", default="steven", help="Entity to query")
    parser.add_argument("--goals", action="store_true", help="Query goals")
    parser.add_argument("--add-goal", help="Add a goal")
    parser.add_argument("--complete-goal", help="Mark goal complete")
    parser.add_argument("--update", nargs=3, metavar=("ENTITY", "KEY", "VALUE"), help="Update knowledge")
    
    args = parser.parse_args()
    
    engine = CognitionEngine()
    
    if args.query:
        print(engine.query(args.query, args.entity))
    elif args.goals:
        print(engine.query_goals())
    elif args.add_goal:
        print(engine.add_goal(args.add_goal))
    elif args.complete_goal:
        print(engine.complete_goal(args.complete_goal))
    elif args.update:
        entity, key, value = args.update
        engine.update_knowledge(entity, key, value)
        print(f"Updated {entity}.{key}")
    else:
        # Default: show Steven summary
        print(engine.query("summary", "steven"))


if __name__ == "__main__":
    main()
