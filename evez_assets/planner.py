#!/usr/bin/env python3
"""
EVEZ Planner - Goal decomposition, task planning, scheduling
Hierarchical task networks, PDDL-like planning, timeline construction
"""

import json
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"

@dataclass
class Task:
    task_id: str
    name: str
    description: str
    priority: TaskPriority
    duration_minutes: int
    prerequisites: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[str] = None
    end_time: Optional[str] = None

@dataclass
class Plan:
    plan_id: str
    goal: str
    tasks: List[Task]
    total_duration: int
    created_at: str

class PlannerEngine:
    """EVEZ Planner - Goal-oriented task planning"""
    
    def __init__(self):
        self.model_name = "EVEZ-Planner-v1"
        self.plans: Dict[str, Plan] = {}
        self.task_library: Dict[str, Task] = {}
    
    def decompose_goal(self, goal: str) -> List[str]:
        """Break down a goal into subgoals"""
        # Simple decomposition patterns
        goal_patterns = {
            "build": ["design", "implement", "test", "deploy"],
            "analyze": ["collect", "process", "interpret", "report"],
            "create": ["plan", "execute", "verify", "deliver"],
            "optimize": ["measure", "identify", "improve", "validate"],
            "research": ["search", "read", "synthesize", "conclude"]
        }
        
        for key, steps in goal_patterns.items():
            if key in goal.lower():
                return steps
        
        return ["assess", "plan", "execute", "review"]
    
    def create_task(self, name: str, description: str, duration: int,
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   prerequisites: Optional[List[str]] = None) -> Task:
        """Create a task"""
        task = Task(
            task_id=f"task_{random.randint(1000, 9999)}",
            name=name,
            description=description,
            priority=priority,
            duration_minutes=duration,
            prerequisites=prerequisites or []
        )
        self.task_library[task.task_id] = task
        return task
    
    def create_plan(self, goal: str, tasks: List[Task]) -> Plan:
        """Create a plan from tasks"""
        # Topologically sort by prerequisites
        sorted_tasks = self._topological_sort(tasks)
        
        total_duration = sum(t.duration_minutes for t in sorted_tasks)
        
        plan = Plan(
            plan_id=f"plan_{random.randint(1000, 9999)}",
            goal=goal,
            tasks=sorted_tasks,
            total_duration=total_duration,
            created_at=datetime.utcnow().isoformat() + "Z"
        )
        
        self.plans[plan.plan_id] = plan
        return plan
    
    def _topological_sort(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by prerequisites"""
        task_map = {t.task_id: t for t in tasks}
        in_degree = {t.task_id: 0 for t in tasks}
        
        # Calculate in-degrees
        for task in tasks:
            for prereq in task.prerequisites:
                if prereq in in_degree:
                    in_degree[task.task_id] += 1
        
        # Kahn's algorithm
        sorted_tasks = []
        queue = [t for t in tasks if in_degree[t.task_id] == 0]
        
        while queue:
            current = queue.pop(0)
            sorted_tasks.append(current)
            
            # Find tasks that depend on this
            for task in tasks:
                if current.task_id in task.prerequisites:
                    in_degree[task.task_id] -= 1
                    if in_degree[task.task_id] == 0:
                        queue.append(task)
        
        return sorted_tasks
    
    def schedule_plan(self, plan_id: str, start_time: str) -> Dict:
        """Schedule plan on timeline"""
        if plan_id not in self.plans:
            return {"error": "Plan not found"}
        
        plan = self.plans[plan_id]
        
        current_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        
        for task in plan.tasks:
            task.start_time = current_time.isoformat()
            current_time += timedelta(minutes=task.duration_minutes)
            task.end_time = current_time.isoformat()
            task.status = TaskStatus.PENDING
        
        return {
            "plan_id": plan_id,
            "start": start_time,
            "end": current_time.isoformat(),
            "tasks": [(t.name, t.start_time, t.end_time) for t in plan.tasks]
        }
    
    def get_critical_path(self, plan_id: str) -> List[str]:
        """Find critical path (longest duration chain)"""
        if plan_id not in self.plans:
            return []
        
        plan = self.plans[plan_id]
        
        # Simple critical path - just longest individual tasks
        tasks_by_duration = sorted(plan.tasks, key=lambda t: t.duration_minutes, reverse=True)
        
        return [t.task_id for t in tasks_by_duration[:5]]
    
    def get_status(self) -> Dict:
        return {
            "model": self.model_name,
            "plans": len(self.plans),
            "tasks": len(self.task_library)
        }


# Demo
if __name__ == "__main__":
    planner = PlannerEngine()
    print("=== EVEZ Planner ===")
    
    # Decompose goal
    subgoals = planner.decompose_goal("build autonomous system")
    print(f"Goal decomposition: {subgoals}")
    
    # Create tasks
    t1 = planner.create_task("design", "Design architecture", 60, TaskPriority.HIGH)
    t2 = planner.create_task("implement", "Write code", 120, TaskPriority.HIGH, [t1.task_id])
    t3 = planner.create_task("test", "Run tests", 45, TaskPriority.MEDIUM, [t2.task_id])
    t4 = planner.create_task("deploy", "Deploy to prod", 30, TaskPriority.MEDIUM, [t3.task_id])
    
    # Create plan
    plan = planner.create_plan("Build EVEZ System", [t1, t2, t3, t4])
    print(f"Plan: {plan.plan_id}, {plan.total_duration} min, {len(plan.tasks)} tasks")
    
    # Schedule
    scheduled = planner.schedule_plan(plan.plan_id, "2026-04-06T04:00:00Z")
    print(f"Scheduled: {scheduled['start']} to {scheduled['end']}")
    
    print(json.dumps(planner.get_status(), indent=2))