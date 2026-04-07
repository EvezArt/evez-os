#!/usr/bin/env python3
"""
EVEZ Simulation - Physics and world simulation
Particles, fluids, cellular automata, world dynamics
"""

import json
import random
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Vector2D:
    x: float
    y: float
    
    def add(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def scale(self, scalar: float) -> "Vector2D":
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def normalize(self) -> "Vector2D":
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

@dataclass
class Particle:
    id: int
    position: Vector2D
    velocity: Vector2D
    mass: float
    radius: float
    color: str

@dataclass
class WorldState:
    timestamp: float
    particles: List[Particle]
    grid: List[List[int]]  # Cellular automaton grid

class SimulationEngine:
    """EVEZ Simulation - Physics and world simulation"""
    
    def __init__(self, width: int = 100, height: int = 100):
        self.model_name = "EVEZ-Simulation-v1"
        self.width = width
        self.height = height
        self.particles: List[Particle] = []
        self.grid: List[List[int]] = [[0] * height for _ in range(width)]
        self.time = 0.0
        self.gravity = Vector2D(0, 0.1)
        self.damping = 0.99
    
    def add_particle(self, x: float, y: float, vx: float = 0, vy: float = 0,
                    mass: float = 1.0, radius: float = 1.0, color: str = "white") -> Particle:
        """Add a particle to the simulation"""
        particle = Particle(
            id=len(self.particles),
            position=Vector2D(x, y),
            velocity=Vector2D(vx, vy),
            mass=mass,
            radius=radius,
            color=color
        )
        self.particles.append(particle)
        return particle
    
    def update_physics(self, dt: float = 1.0):
        """Update particle physics"""
        for p in self.particles:
            # Apply gravity
            p.velocity = p.velocity.add(self.gravity)
            
            # Update position
            p.position = p.position.add(p.velocity.scale(dt))
            
            # Damping
            p.velocity = p.velocity.scale(self.damping)
            
            # Boundary collision
            if p.position.x < 0:
                p.position.x = 0
                p.velocity.x *= -0.8
            elif p.position.x > self.width:
                p.position.x = self.width
                p.velocity.x *= -0.8
                
            if p.position.y < 0:
                p.position.y = 0
                p.velocity.y *= -0.8
            elif p.position.y > self.height:
                p.position.y = self.height
                p.velocity.y *= -0.8
        
        self.time += dt
    
    def update_cellular_automaton(self, rule: str = "game_of_life"):
        """Update cellular automaton grid"""
        new_grid = [[0] * self.height for _ in range(self.width)]
        
        for x in range(self.width):
            for y in range(self.height):
                neighbors = self._count_neighbors(x, y)
                current = self.grid[x][y]
                
                if rule == "game_of_life":
                    # Conway's Game of Life rules
                    if current == 1:
                        new_grid[x][y] = 1 if neighbors in [2, 3] else 0
                    else:
                        new_grid[x][y] = 1 if neighbors == 3 else 0
                
                elif rule == "wireworld":
                    # Wireworld circuit simulation
                    if current == 0:  # Empty
                        new_grid[x][y] = 0
                    elif current == 1:  # Electron head
                        new_grid[x][y] = 2
                    elif current == 2:  # Electron tail
                        new_grid[x][y] = 3
                    elif current == 3:  # Conductor
                        new_grid[x][y] = 1 if neighbors in [1, 2] else 3
                
                elif rule == "rain":
                    # Rain simulation
                    if current == 0 and random.random() < 0.01:
                        new_grid[x][y] = 1
                    elif current == 1:
                        if y < self.height - 1 and self.grid[x][y + 1] == 0:
                            new_grid[x][y + 1] = 1
                        elif random.random() < 0.1:
                            new_grid[x][y] = 0
                    else:
                        new_grid[x][y] = current
        
        self.grid = new_grid
    
    def _count_neighbors(self, x: int, y: int) -> int:
        """Count alive neighbors for CA"""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.grid[nx][ny] == 1:
                        count += 1
        return count
    
    def apply_force_at(self, x: float, y: float, force: Vector2D, radius: float = 10.0):
        """Apply force to particles near a point"""
        for p in self.particles:
            dx = p.position.x - x
            dy = p.position.y - y
            dist = math.sqrt(dx ** 2 + dy ** 2)
            
            if dist < radius:
                # Scale force by distance
                scale = 1 - (dist / radius)
                p.velocity = p.velocity.add(force.scale(scale))
    
    def get_state(self) -> WorldState:
        """Get current world state"""
        return WorldState(
            timestamp=self.time,
            particles=list(self.particles),
            grid=self.grid
        )
    
    def get_particle_stats(self) -> Dict:
        """Get particle statistics"""
        if not self.particles:
            return {"count": 0}
        
        avg_speed = sum(p.velocity.magnitude() for p in self.particles) / len(self.particles)
        
        return {
            "count": len(self.particles),
            "avg_speed": avg_speed,
            "time": self.time
        }
    
    def get_grid_stats(self) -> Dict:
        """Get cellular automaton statistics"""
        alive = sum(sum(row) for row in self.grid)
        return {
            "width": self.width,
            "height": self.height,
            "alive_cells": alive,
            "density": alive / (self.width * self.height)
        }


# Demo
if __name__ == "__main__":
    sim = SimulationEngine(50, 50)
    print("=== EVEZ Simulation ===")
    
    # Add particles
    for _ in range(20):
        sim.add_particle(
            random.uniform(10, 40),
            random.uniform(10, 40),
            random.uniform(-2, 2),
            random.uniform(-2, 2)
        )
    
    # Physics steps
    for _ in range(10):
        sim.update_physics(1.0)
    
    print(f"Particle stats: {sim.get_particle_stats()}")
    
    # CA steps
    for _ in range(5):
        sim.update_cellular_automaton("game_of_life")
    
    print(f"Grid stats: {sim.get_grid_stats()}")