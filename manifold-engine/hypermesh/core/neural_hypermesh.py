#!/usr/bin/env python3
"""
Neural Hypermesh - Multi-Modal Learning Network
Routes between text, code, math, reasoning, and creation modalities.
"""
import random
import hashlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class ModalNode:
    """A node that processes one modality"""
    name: str
    modality: str
    weights: List[float]
    bias: float
    active: bool = True
    usage_count: int = 0
    success_rate: float = 0.5

@dataclass
class HyperEdge:
    """Connection between modalities"""
    source: str
    target: str
    weight: float = 1.0
    plasticity: float = 0.1

class NeuralHypermesh:
    """
    Neural hypermesh that learns to route between modalities.
    Each node processes one type of content.
    Edges transfer and transform knowledge.
    """
    
    MODALITIES = ["text", "code", "math", "reasoning", "creation", "research"]
    
    def __init__(self, embed_dim: int = 64):
        self.embed_dim = embed_dim
        self.nodes: Dict[str, ModalNode] = {}
        self.edges: Dict[Tuple[str, str], HyperEdge] = {}
        self.activity = defaultdict(float)
        
        # Initialize nodes
        for mod in self.MODALITIES:
            node = ModalNode(
                name=mod,
                modality=mod,
                weights=[random.uniform(-0.1, 0.1) for _ in range(embed_dim)],
                bias=0.0
            )
            self.nodes[mod] = node
        
        # Initialize edges (fully connected)
        for s in self.MODALITIES:
            for t in self.MODALITIES:
                if s != t:
                    self.edges[(s, t)] = HyperEdge(s, t, 1.0)
    
    def _embed(self, text: str) -> List[float]:
        """Simple embedding (use proper embeddings in production)"""
        vec = [0.0] * self.embed_dim
        for i, c in enumerate(text[:self.embed_dim]):
            vec[i % self.embed_dim] += ord(c) / 255.0
        total = sum(vec) + 1
        return [v/total for v in vec]
    
    def _classify_modality(self, content: str) -> str:
        """Classify content's primary modality"""
        content = content.lower()
        
        if any(k in content for k in ["def ", "class ", "import ", "function ", "=>", "{"]):
            return "code"
        
        if any(k in content for k in ["=", "+", "-", "*", "/", "equation", "solve", "∫", "∑"]):
            return "math"
        
        if any(k in content for k in ["why", "because", "therefore", "thus", "conclude", "logic"]):
            return "reasoning"
        
        if any(k in content for k in ["study", "research", "paper", "data", "evidence", "analyze"]):
            return "research"
        
        if any(k in content for k in ["create", "write", "poem", "story", "design", "art"]):
            return "creation"
        
        return "text"
    
    def process(self, content: str, target_modality: Optional[str] = None) -> Dict:
        """Process content through the mesh"""
        input_mod = self._classify_modality(content)
        target = target_modality or input_mod
        embed = self._embed(content)
        
        node = self.nodes.get(input_mod)
        if node:
            node.usage_count += 1
        
        return {
            "input_modality": input_mod,
            "target_modality": target,
            "routed": target,
            "embedding": embed[:5],
            "available_routes": self._get_routes(input_mod)
        }
    
    def _get_routes(self, from_mod: str) -> List[str]:
        """Get available routes from modality"""
        routes = []
        for (s, t), edge in self.edges.items():
            if s == from_mod and edge.weight > 0.3:
                routes.append(t)
        return routes
    
    def transfer(self, from_mod: str, to_mod: str, strength: float = 1.0):
        """Strengthen transfer between modalities"""
        key = (from_mod, to_mod)
        if key in self.edges:
            self.edges[key].weight = min(2.0, self.edges[key].weight + strength * 0.1)
    
    def learn(self, from_mod: str, to_mod: str, success: bool):
        """Learn from transfer outcomes"""
        key = (from_mod, to_mod)
        if key in self.edges:
            edge = self.edges[key]
            if success:
                edge.weight = min(2.0, edge.weight * (1 + edge.plasticity))
            else:
                edge.weight = max(0.1, edge.weight * (1 - edge.plasticity))
            
            node = self.nodes.get(to_mod)
            if node:
                node.success_rate = node.success_rate * 0.9 + (1.0 if success else 0.0) * 0.1
    
    def route_through(self, content: str) -> List[str]:
        """Determine best route through mesh"""
        input_mod = self._classify_modality(content)
        route = [input_mod]
        
        if self._classify_modality(content) == "reasoning" and len(content) > 100:
            route.insert(0, "research")
        
        if self._classify_modality(content) == "code":
            route.append("text")
        
        return route
    
    def get_topology(self) -> Dict:
        """Get mesh topology for visualization"""
        return {
            "nodes": [
                {"id": n.name, "modality": n.modality, "usage": n.usage_count, "success": n.success_rate}
                for n in self.nodes.values()
            ],
            "edges": [
                {"from": e.source, "to": e.target, "weight": e.weight}
                for e in self.edges.values()
            ]
        }

def demo_hypermesh():
    """Demo the neural hypermesh"""
    mesh = NeuralHypermesh()
    
    print("=" * 50)
    print("NEURAL HYPERMESH")
    print("=" * 50)
    
    tests = [
        "def hello(): return 'world'",
        "Why does quantum entanglement work?",
        "Calculate ∫x²dx",
        "Write a poem about AI",
        "Research shows that machine learning",
    ]
    
    for content in tests:
        result = mesh.process(content)
        route = mesh.route_through(content)
        
        print(f"\n📝 {content[:40]}...")
        print(f"   Modality: {result['input_modality']}")
        print(f"   Route: → ".join(route))
    
    print("\n📊 Topology:")
    topo = mesh.get_topology()
    print(f"   Nodes: {len(topo['nodes'])}")
    print(f"   Edges: {len(topo['edges'])}")
    
    return mesh

if __name__ == "__main__":
    demo_hypermesh()