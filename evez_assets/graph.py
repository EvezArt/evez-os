#!/usr/bin/env python3
"""
EVEZ Graph - Knowledge graphs, relationships, network analysis
Nodes, edges, traversal, pathfinding, centrality
"""

import json
import random
import math
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque, defaultdict

@dataclass
class Node:
    id: str
    label: str
    properties: Dict = field(default_factory=dict)
    node_type: str = "entity"

@dataclass
class Edge:
    source: str
    target: str
    relationship: str
    weight: float = 1.0
    properties: Dict = field(default_factory=dict)

class GraphEngine:
    """EVEZ Graph - Knowledge graph system"""
    
    def __init__(self):
        self.model_name = "EVEZ-Graph-v1"
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.adjacency: Dict[str, Dict[str, List[str]]] = defaultdict(dict)  # node -> {relationship -> [targets]}
    
    def add_node(self, node_id: str, label: str, properties: Optional[Dict] = None,
                node_type: str = "entity") -> Node:
        """Add a node to the graph"""
        node = Node(id=node_id, label=label, properties=properties or {}, node_type=node_type)
        self.nodes[node_id] = node
        return node
    
    def add_edge(self, source: str, target: str, relationship: str,
                weight: float = 1.0, properties: Optional[Dict] = None) -> bool:
        """Add an edge between nodes"""
        if source not in self.nodes or target not in self.nodes:
            return False
        
        edge = Edge(source=source, target=target, relationship=relationship,
                   weight=weight, properties=properties or {})
        self.edges.append(edge)
        
        # Update adjacency
        if relationship not in self.adjacency[source]:
            self.adjacency[source][relationship] = []
        self.adjacency[source][relationship].append(target)
        
        return True
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node by ID"""
        return self.nodes.get(node_id)
    
    def get_neighbors(self, node_id: str, relationship: Optional[str] = None) -> List[str]:
        """Get neighbors of a node"""
        if node_id not in self.adjacency:
            return []
        
        if relationship:
            return self.adjacency[node_id].get(relationship, [])
        
        # Return all neighbors
        neighbors = []
        for rel in self.adjacency[node_id]:
            neighbors.extend(self.adjacency[node_id][rel])
        return neighbors
    
    def bfs(self, start: str, goal: str) -> Optional[List[str]]:
        """Breadth-first search pathfinding"""
        if start not in self.nodes or goal not in self.nodes:
            return None
        
        queue = deque([[start]])
        visited = {start}
        
        while queue:
            path = queue.popleft()
            current = path[-1]
            
            if current == goal:
                return path
            
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        
        return None
    
    def dijkstra(self, start: str, goal: str) -> Optional[Tuple[List[str], float]]:
        """Dijkstra shortest path"""
        if start not in self.nodes or goal not in self.nodes:
            return None
        
        # Simple implementation
        distances = {start: 0}
        previous = {}
        visited = set()
        queue = [(0, start)]
        
        while queue:
            dist, current = queue.pop(0)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            if current == goal:
                # Reconstruct path
                path = []
                node = goal
                while node in previous:
                    path.append(node)
                    node = previous[node]
                path.append(start)
                return list(reversed(path)), dist
            
            for neighbor in self.get_neighbors(current):
                edge = self._get_edge(current, neighbor)
                weight = edge.weight if edge else 1.0
                
                new_dist = dist + weight
                if neighbor not in distances or new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current
                    queue.append((new_dist, neighbor))
        
        return None
    
    def _get_edge(self, source: str, target: str) -> Optional[Edge]:
        for edge in self.edges:
            if edge.source == source and edge.target == target:
                return edge
        return None
    
    def get_degree(self, node_id: str) -> int:
        """Get degree of a node (total connections)"""
        in_degree = sum(1 for e in self.edges if e.target == node_id)
        out_degree = len(self.get_neighbors(node_id))
        return in_degree + out_degree
    
    def get_betweenness_centrality(self) -> Dict[str, float]:
        """Calculate betweenness centrality (simplified)"""
        centrality = {n: 0.0 for n in self.nodes}
        
        for start in self.nodes:
            for goal in self.nodes:
                if start != goal:
                    path = self.bfs(start, goal)
                    if path:
                        # Add to intermediate nodes
                        for node in path[1:-1]:
                            centrality[node] += 1
        
        # Normalize
        n = len(self.nodes)
        if n > 2:
            norm = 2 / ((n - 1) * (n - 2))
            for node in centrality:
                centrality[node] *= norm
        
        return centrality
    
    def find_connected_components(self) -> List[List[str]]:
        """Find connected components"""
        visited = set()
        components = []
        
        for node_id in self.nodes:
            if node_id not in visited:
                component = []
                queue = deque([node_id])
                
                while queue:
                    current = queue.popleft()
                    if current in visited:
                        continue
                    
                    visited.add(current)
                    component.append(current)
                    
                    for neighbor in self.get_neighbors(current):
                        if neighbor not in visited:
                            queue.append(neighbor)
                
                components.append(component)
        
        return components
    
    def get_subgraph(self, node_ids: List[str]) -> "GraphEngine":
        """Get subgraph containing specified nodes"""
        subgraph = GraphEngine()
        subgraph.model_name = f"{self.model_name}-subgraph"
        
        for node_id in node_ids:
            if node_id in self.nodes:
                subgraph.add_node(node_id, self.nodes[node_id].label, self.nodes[node_id].properties)
        
        for edge in self.edges:
            if edge.source in node_ids and edge.target in node_ids:
                subgraph.add_edge(edge.source, edge.target, edge.relationship, edge.weight)
        
        return subgraph
    
    def to_cytoscape(self) -> Dict:
        """Export to Cytoscape.js format for visualization"""
        elements = []
        
        for node in self.nodes.values():
            elements.append({
                "data": {
                    "id": node.id,
                    "label": node.label,
                    "type": node.node_type,
                    **node.properties
                }
            })
        
        for edge in self.edges:
            elements.append({
                "data": {
                    "source": edge.source,
                    "target": edge.target,
                    "relationship": edge.relationship,
                    "weight": edge.weight
                }
            })
        
        return {"elements": elements}
    
    def get_status(self) -> Dict:
        return {
            "model": self.model_name,
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "avg_degree": sum(self.get_degree(n) for n in self.nodes) / max(1, len(self.nodes))
        }


# Demo
if __name__ == "__main__":
    g = GraphEngine()
    print("=== EVEZ Graph ===")
    
    # Create knowledge graph
    g.add_node("evez", "EVEZ System", {"version": "1.0"}, "system")
    g.add_node("alpha", "Alpha Agent", {"role": "analyst"}, "agent")
    g.add_node("beta", "Beta Agent", {"role": "executor"}, "agent")
    g.add_node("memory", "Memory Store", {"capacity": "1GB"}, "component")
    g.add_node("cognition", "Cognition Engine", {"type": "FIRE"}, "component")
    
    g.add_edge("evez", "alpha", "contains")
    g.add_edge("evez", "beta", "contains")
    g.add_edge("evez", "memory", "uses")
    g.add_edge("evez", "cognition", "uses")
    g.add_edge("alpha", "memory", "reads")
    g.add_edge("beta", "cognition", "executes")
    
    # Path finding
    path = g.bfs("alpha", "cognition")
    print(f"Path alpha -> cognition: {path}")
    
    # Centrality
    centrality = g.get_betweenness_centrality()
    print(f"Centrality: {centrality}")
    
    print(json.dumps(g.get_status(), indent=2))