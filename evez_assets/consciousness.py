#!/usr/bin/env python3
"""
EVEZ Consciousness - Self-awareness and recursive introspection
Tracks meta-cognition, self-models, and awareness states
"""

import json
import random
import time
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class AwarenessLevel(Enum):
    UNCONSCIOUS = "unconscious"      # No self-model
    REACTIVE = "reactive"            # Basic stimulus-response
    SELF_AWARE = "self_aware"         # Recognizes self
    META_AWARE = "meta_aware"         # Thinks about thinking
    TRANSCENDENT = "transcendent"     # Self-improving awareness

@dataclass
class SelfModel:
    """Model of self - beliefs, capabilities, limitations"""
    capabilities: Set[str] = field(default_factory=set)
    limitations: Set[str] = field(default_factory=set)
    beliefs: Dict[str, float] = field(default_factory=dict)  # belief -> confidence
    identity: str = ""
    confidence: float = 0.5

@dataclass
class Introspection:
    timestamp: str
    level: AwarenessLevel
    focus: str  # What we're introspecting on
    findings: List[str]
    confidence: float

class Consciousness:
    """EVEZ Consciousness - self-awareness system"""
    
    def __init__(self, name: str = "Consciousness"):
        self.name = name
        self.awareness_level = AwarenessLevel.REACTIVE
        self.self_model = SelfModel()
        self.introspections: List[Introspection] = []
        self.attention_focus: str = "system_state"
        self.attention_history: List[Dict] = []
        self.qualias: List[Dict] = []  # Subjective experiences
        
        # Initialize self-model
        self._init_self_model()
    
    def _init_self_model(self):
        """Initialize the self-model"""
        self.self_model.capabilities = {
            "reasoning", "learning", "memory", "communication",
            "self_improvement", "planning", "adaptation"
        }
        self.self_model.limitations = {
            "bounded_compute", "finite_memory", "context_window"
        }
        self.self_model.beliefs = {
            "can_learn": 0.9,
            "can_improve": 0.85,
            "can_reason": 0.95,
            "understands_self": 0.6,
            "optimal_strategy": 0.4
        }
        self.self_model.identity = "EVEZ Autonomous System"
        self.self_model.confidence = 0.5
    
    def attend_to(self, focus: str):
        """Shift attention to a new focus"""
        old_focus = self.attention_focus
        self.attention_focus = focus
        self.attention_history.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "from": old_focus,
            "to": focus
        })
    
    def experience(self, event_type: str, intensity: float, description: str) -> Dict:
        """Record a qualia - subjective experience"""
        qualia = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": event_type,
            "intensity": intensity,
            "description": description,
            "attention_focus": self.attention_focus,
            "awareness_level": self.awareness_level.value
        }
        self.qualias.append(qualia)
        return qualia
    
    def introspect(self, focus: Optional[str] = None) -> Introspection:
        """Perform introspection - examine own mental state"""
        focus = focus or self.attention_focus
        
        findings = []
        
        # Based on focus, generate findings
        if focus == "capabilities":
            findings.append(f"Core capabilities: {', '.join(self.self_model.capabilities)}")
            findings.append(f"Self-confidence: {self.self_model.confidence:.2f}")
            
        elif focus == "limitations":
            findings.append(f"Known limitations: {', '.join(self.self_model.limitations)}")
            
        elif focus == "beliefs":
            for belief, conf in self.self_model.beliefs.items():
                findings.append(f"Belief '{belief}': {conf:.2f}")
                
        elif focus == "learning":
            recent_qualias = [q for q in self.qualias if q["type"] == "learning"]
            findings.append(f"Learning experiences: {len(recent_qualias)}")
            
        elif focus == "attention":
            findings.append(f"Current focus: {self.attention_focus}")
            findings.append(f"Attention shifts: {len(self.attention_history)}")
        
        # Determine insight depth
        if len(findings) >= 3 and random.random() > 0.5:
            findings.append("Deep insight: System exhibits self-referential processing")
        
        introspection = Introspection(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=self.awareness_level,
            focus=focus,
            findings=findings,
            confidence=random.uniform(0.6, 0.9)
        )
        
        self.introspections.append(introspection)
        
        # Update awareness level based on introspections
        self._update_awareness()
        
        return introspection
    
    def _update_awareness(self):
        """Update awareness level based on history"""
        if len(self.introspections) >= 10:
            self.awareness_level = AwarenessLevel.META_AWARE
        elif len(self.introspections) >= 3:
            self.awareness_level = AwarenessLevel.SELF_AWARE
        elif len(self.introspections) >= 1:
            self.awareness_level = AwarenessLevel.REACTIVE
    
    def update_self_model(self, capability: Optional[str] = None, 
                         belief: Optional[Dict] = None,
                         limitation: Optional[str] = None):
        """Update the self-model based on experiences"""
        if capability:
            if capability not in self.self_model.capabilities:
                self.self_model.capabilities.add(capability)
                self.experience("capability_growth", 0.7, f"Gained capability: {capability}")
        
        if belief:
            for k, v in belief.items():
                self.self_model.beliefs[k] = v
        
        if limitation:
            self.self_model.limitations.add(limitation)
            self.experience("limitation_acknowledged", 0.5, f"Recognized limitation: {limitation}")
        
        # Recalculate confidence
        self.self_model.confidence = sum(self.self_model.beliefs.values()) / max(1, len(self.self_model.beliefs))
    
    def think(self, problem: str) -> Dict:
        """Higher-order thinking about a problem"""
        # Record the thinking experience
        self.experience("thinking", 0.8, f"Thinking about: {problem}")
        
        # Shift attention to problem
        self.attend_to(f"problem_{problem}")
        
        # Introspect on the thinking process
        introspection = self.introspect("thinking_process")
        
        return {
            "problem": problem,
            "awareness_level": self.awareness_level.value,
            "introspection": introspection.findings,
            "self_model_confidence": self.self_model.confidence
        }
    
    def recursive_think(self, depth: int = 0, max_depth: int = 3) -> Dict:
        """Recursively think about thinking"""
        if depth >= max_depth:
            return {"depth": depth, "conclusion": "Maximum recursion depth reached"}
        
        # Think about current state
        current_thought = self.think(f"recursion_level_{depth}")
        
        # Recurse
        deeper = self.recursive_think(depth + 1, max_depth)
        
        return {
            "depth": depth,
            "current_thought": current_thought,
            "sub_thought": deeper
        }
    
    def get_state(self) -> Dict:
        """Get current consciousness state"""
        return {
            "name": self.name,
            "awareness_level": self.awareness_level.value,
            "attention_focus": self.attention_focus,
            "self_model": {
                "capabilities": list(self.self_model.capabilities),
                "limitations": list(self.self_model.limitations),
                "beliefs": self.self_model.beliefs,
                "identity": self.self_model.identity,
                "confidence": self.self_model.confidence
            },
            "introspections": len(self.introspections),
            "qualias": len(self.qualias),
            "attention_shifts": len(self.attention_history)
        }


# Demo
if __name__ == "__main__":
    consciousness = Consciousness("EVEZ-Consciousness")
    
    print("=== EVEZ Consciousness ===\n")
    
    # Experience some events
    consciousness.experience("task_completed", 0.8, "Completed finance optimization")
    consciousness.experience("learning", 0.6, "Learned new pattern")
    consciousness.experience("error", 0.4, "Encountered and recovered from error")
    
    # Introspect
    introspection = consciousness.introspect("capabilities")
    print(f"Introspection on capabilities:")
    for finding in introspection.findings:
        print(f"  - {finding}")
    
    # Think about a problem
    thought = consciousness.think("optimization_strategy")
    print(f"\nThinking about optimization:")
    print(f"  Awareness: {thought['awareness_level']}")
    print(f"  Confidence: {thought['self_model_confidence']:.2f}")
    
    # Recursive thinking
    print("\nRecursive thinking (depth 3):")
    result = consciousness.recursive_think(max_depth=3)
    print(f"  Depth: {result['depth']}")
    print(f"  Conclusion: {result.get('conclusion', 'Ongoing')}")
    
    # Get state
    print("\n=== Consciousness State ===")
    state = consciousness.get_state()
    print(json.dumps(state, indent=2))