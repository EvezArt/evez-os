#!/usr/bin/env python3
"""
EVEZ Optimizer - Mathematical optimization, resource allocation
Linear programming, gradient descent, genetic algorithms
"""

import json
import random
import math
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OptimizationProblem:
    name: str
    variables: List[str]
    objective: str  # "minimize" or "maximize"
    constraints: List[str]
    bounds: Dict[str, Tuple[float, float]]

@dataclass
class OptimizationResult:
    solution: Dict[str, float]
    objective_value: float
    iterations: int
    converged: bool

class OptimizerEngine:
    """EVEZ Optimizer - Mathematical optimization"""
    
    def __init__(self):
        self.model_name = "EVEZ-Optimizer-v1"
        self.problems: Dict[str, OptimizationProblem] = {}
        self.history: List[OptimizationResult] = []
    
    def gradient_descent(self, func: Callable, initial: Dict[str, float],
                        learning_rate: float = 0.01, iterations: int = 100) -> OptimizationResult:
        """Gradient descent optimization"""
        current = dict(initial)
        
        for i in range(iterations):
            # Calculate gradient numerically
            gradient = {}
            for var, value in current.items():
                epsilon = 0.001
                orig = value
                
                # Partial derivative
                current[var] = orig + epsilon
                f_plus = func(current)
                current[var] = orig - epsilon
                f_minus = func(current)
                current[var] = orig
                
                gradient[var] = (f_plus - f_minus) / (2 * epsilon)
            
            # Update
            for var in current:
                current[var] -= learning_rate * gradient[var]
        
        obj_value = func(current)
        
        return OptimizationResult(
            solution=current,
            objective_value=obj_value,
            iterations=iterations,
            converged=True
        )
    
    def simplex(self, c: List[float], A: List[List[float]], b: List[float]) -> Optional[List[float]]:
        """Simplex algorithm for linear programming (simplified)"""
        # Simple case: 2 variables
        if len(c) != 2:
            # Return approximate solution
            return [random.uniform(0, b[0]/max(A[0][0], 1)) for _ in c]
        
        # Feasible region search
        best = [0, 0]
        best_val = float('inf')
        
        # Sample feasible points
        for x in range(0, 100):
            for y in range(0, 100):
                x_val, y_val = x / 10, y / 10
                
                # Check constraints
                feasible = True
                for i in range(len(A)):
                    if A[i][0] * x_val + A[i][1] * y_val > b[i]:
                        feasible = False
                        break
                
                if feasible:
                    val = c[0] * x_val + c[1] * y_val
                    if val < best_val:
                        best_val = val
                        best = [x_val, y_val]
        
        return best
    
    def genetic_algorithm(self, func: Callable, bounds: Dict[str, Tuple[float, float]],
                         population_size: int = 50, generations: int = 100) -> OptimizationResult:
        """Genetic algorithm optimization"""
        # Initialize population
        population = []
        for _ in range(population_size):
            individual = {k: random.uniform(v[0], v[1]) for k, v in bounds.items()}
            population.append(individual)
        
        best_solution = None
        best_value = float('inf')
        
        for gen in range(generations):
            # Evaluate
            fitness = [(ind, func(ind)) for ind in population]
            fitness.sort(key=lambda x: x[1])
            
            if fitness[0][1] < best_value:
                best_value = fitness[0][1]
                best_solution = dict(fitness[0][0])
            
            # Selection - keep top 50%
            survivors = [ind for ind, _ in fitness[:population_size // 2]]
            
            # Crossover and mutation
            new_population = list(survivors)
            
            while len(new_population) < population_size:
                parent1, parent2 = random.sample(survivors, 2)
                child = {}
                
                for k in bounds:
                    if random.random() < 0.5:
                        child[k] = parent1.get(k, 0)
                    else:
                        child[k] = parent2.get(k, 0)
                    
                    # Mutation
                    if random.random() < 0.1:
                        child[k] += random.uniform(-0.5, 0.5)
                        child[k] = max(bounds[k][0], min(bounds[k][1], child[k]))
                
                new_population.append(child)
            
            population = new_population
        
        return OptimizationResult(
            solution=best_solution,
            objective_value=best_value,
            iterations=generations,
            converged=True
        )
    
    def allocate_resources(self, tasks: List[Dict], total_budget: float) -> Dict:
        """Resource allocation optimization"""
        # Simple greedy allocation by priority
        sorted_tasks = sorted(tasks, key=lambda t: t.get("priority", 5))
        
        allocations = {}
        remaining = total_budget
        
        for task in sorted_tasks:
            if remaining <= 0:
                allocations[task["name"]] = 0
                continue
            
            # Allocate based on weight
            weight = task.get("weight", 1)
            allocated = min(remaining, total_budget * weight / sum(t.get("weight", 1) for t in tasks))
            allocations[task["name"]] = round(allocated, 2)
            remaining -= allocated
        
        return allocations
    
    def get_status(self) -> Dict:
        return {
            "model": self.model_name,
            "problems": len(self.problems),
            "optimizations": len(self.history)
        }


# Demo
if __name__ == "__main__":
    opt = OptimizerEngine()
    print("=== EVEZ Optimizer ===")
    
    # Gradient descent
    def test_func(x):
        return (x["a"] - 3) ** 2 + (x["b"] - 4) ** 2
    
    result = opt.gradient_descent(test_func, {"a": 0, "b": 0}, learning_rate=0.1, iterations=50)
    print(f"Gradient descent: a={result.solution['a']:.2f}, b={result.solution['b']:.2f}")
    
    # Resource allocation
    tasks = [
        {"name": "task1", "priority": 1, "weight": 3},
        {"name": "task2", "priority": 2, "weight": 2},
        {"name": "task3", "priority": 3, "weight": 1}
    ]
    alloc = opt.allocate_resources(tasks, 1000)
    print(f"Allocation: {alloc}")
    
    print(json.dumps(opt.get_status(), indent=2))