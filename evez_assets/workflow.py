#!/usr/bin/env python3
"""
EVEZ Workflow - Business process automation
Task pipelines, approvals, state machines, BPMN-like flows
"""

import json
import random
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class NodeType(Enum):
    START = "start"
    TASK = "task"
    DECISION = "decision"
    APPROVAL = "approval"
    PARALLEL = "parallel"
    END = "end"

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_APPROVAL = "waiting_approval"

@dataclass
class WorkflowNode:
    node_id: str
    node_type: NodeType
    name: str
    config: Dict = field(default_factory=dict)
    next_nodes: List[str] = field(default_factory=list)

@dataclass
class WorkflowInstance:
    instance_id: str
    workflow_name: str
    current_node: str
    status: str
    created_at: str
    updated_at: str
    variables: Dict = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)

class WorkflowEngine:
    """EVEZ Workflow - Process automation system"""
    
    def __init__(self):
        self.model_name = "EVEZ-Workflow-v1"
        self.workflows: Dict[str, List[WorkflowNode]] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        
    def define_workflow(self, name: str, nodes: List[WorkflowNode]) -> bool:
        """Define a new workflow"""
        self.workflows[name] = nodes
        return True
    
    def create_instance(self, workflow_name: str, variables: Optional[Dict] = None) -> Optional[str]:
        """Create a new workflow instance"""
        if workflow_name not in self.workflows:
            return None
        
        nodes = self.workflows[workflow_name]
        start_node = nodes[0]  # Assume first node is start
        
        instance = WorkflowInstance(
            instance_id=f"inst_{random.randint(100000, 999999)}",
            workflow_name=workflow_name,
            current_node=start_node.node_id,
            status="running",
            variables=variables or {},
            created_at=datetime.utcnow().isoformat() + "Z",
            updated_at=datetime.utcnow().isoformat() + "Z"
        )
        
        self.instances[instance.instance_id] = instance
        return instance.instance_id
    
    def execute_node(self, instance_id: str) -> bool:
        """Execute current node of an instance"""
        if instance_id not in self.instances:
            return False
        
        instance = self.instances[instance_id]
        
        # Get current node
        nodes = self.workflows[instance.workflow_name]
        current = None
        for n in nodes:
            if n.node_id == instance.current_node:
                current = n
                break
        
        if not current:
            return False
        
        # Record execution
        history_entry = {
            "node_id": current.node_id,
            "node_name": current.name,
            "node_type": current.node_type.value,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "variables": dict(instance.variables)
        }
        instance.history.append(history_entry)
        
        # Execute based on node type
        if current.node_type == NodeType.TASK:
            # Simulate task execution
            instance.variables["last_task"] = current.name
            instance.variables["last_result"] = "completed"
            
        elif current.node_type == NodeType.DECISION:
            # Random decision
            decision = random.choice(current.next_nodes)
            current = next((n for n in nodes if n.node_id == decision), current)
            
        elif current.node_type == NodeType.APPROVAL:
            instance.status = "waiting_approval"
            history_entry["status"] = "waiting_approval"
            return True
        
        elif current.node_type == NodeType.END:
            instance.status = "completed"
            instance.current_node = current.node_id
            return True
        
        # Move to next node
        if current.next_nodes:
            instance.current_node = random.choice(current.next_nodes)
        
        instance.updated_at = datetime.utcnow().isoformat() + "Z"
        return True
    
    def approve_task(self, instance_id: str) -> bool:
        """Approve a waiting task"""
        if instance_id not in self.instances:
            return False
        
        instance = self.instances[instance_id]
        
        if instance.status != "waiting_approval":
            return False
        
        instance.status = "running"
        
        # Move to next node
        nodes = self.workflows[instance.workflow_name]
        for n in nodes:
            if n.node_id == instance.current_node and n.next_nodes:
                instance.current_node = random.choice(n.next_nodes)
                break
        
        instance.updated_at = datetime.utcnow().isoformat() + "Z"
        return True
    
    def run_instance(self, instance_id: str, steps: int = 10) -> Dict:
        """Run an instance until completion or max steps"""
        for _ in range(steps):
            if instance_id not in self.instances:
                break
            
            instance = self.instances[instance_id]
            
            if instance.status in ["completed", "failed"]:
                break
            
            if not self.execute_node(instance_id):
                break
        
        return {
            "instance_id": instance_id,
            "status": instance.status,
            "current_node": instance.current_node,
            "steps_executed": len(instance.history),
            "variables": instance.variables
        }
    
    def get_status(self) -> Dict:
        return {
            "model": self.model_name,
            "workflows": len(self.workflows),
            "instances": len(self.instances),
            "running": len([i for i in self.instances.values() if i.status == "running"]),
            "completed": len([i for i in self.instances.values() if i.status == "completed"])
        }


# Demo
if __name__ == "__main__":
    wf = WorkflowEngine()
    print("=== EVEZ Workflow ===")
    
    # Define workflow
    nodes = [
        WorkflowNode("start", NodeType.START, "Start"),
        WorkflowNode("task1", NodeType.TASK, "Process Data"),
        WorkflowNode("decide", NodeType.DECISION, "Check Result"),
        WorkflowNode("task2", NodeType.TASK, "Send Notification"),
        WorkflowNode("approve", NodeType.APPROVAL, "Manager Approval"),
        WorkflowNode("end", NodeType.END, "Complete")
    ]
    nodes[1].next_nodes = ["decide"]
    nodes[2].next_nodes = ["task2", "end"]
    nodes[3].next_nodes = ["approve"]
    nodes[4].next_nodes = ["end"]
    
    wf.define_workflow("data_pipeline", nodes)
    
    # Create and run instance
    inst_id = wf.create_instance("data_pipeline", {"input": "test_data"})
    if inst_id:
        result = wf.run_instance(inst_id, steps=10)
        print(f"Instance: {inst_id}")
        print(f"Status: {result['status']}, Steps: {result['steps_executed']}")
    
    print(json.dumps(wf.get_status(), indent=2))