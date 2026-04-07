#!/usr/bin/env python3
"""
EVEZ Network Module - Peer-to-peer communication, sync, and distributed state
Enables multi-instance coordination and state sharing
"""

import json
import time
import random
import uuid
import hashlib
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import socket
import threading

class MessageType(Enum):
    HEARTBEAT = "heartbeat"
    SYNC = "sync"
    PROPOSE = "propose"
    VOTE = "vote"
    COMMIT = "commit"
    BROADCAST = "broadcast"

class NodeStatus(Enum):
    ACTIVE = "active"
    SUSPECTED = "suspected"
    FAILED = "failed"

@dataclass
class Node:
    id: str
    address: str
    port: int
    status: NodeStatus
    last_seen: float
    version: int
    capabilities: List[str] = field(default_factory=list)

@dataclass
class Message:
    id: str
    msg_type: MessageType
    sender: str
    recipient: Optional[str]  # None = broadcast
    timestamp: str
    payload: Dict
    signature: str = ""

class NetworkMesh:
    """EVEZ-style peer-to-peer network mesh"""
    
    def __init__(self, node_id: str, port: int = 0):
        self.node_id = node_id
        self.port = port
        self.nodes: Dict[str, Node] = {}
        self.message_log: List[Message] = []
        self.pending_proposals: Dict[str, Dict] = {}
        self.votes: Dict[str, Set[str]] = {}  # proposal_id -> set of voters
        self.committed: Set[str] = set()
        
        # Register self as a node
        self.nodes[node_id] = Node(
            id=node_id,
            address="127.0.0.1",
            port=port,
            status=NodeStatus.ACTIVE,
            last_seen=time.time(),
            version=1,
            capabilities=["spine", "agent", "cognition"]
        )
    
    def discover_node(self, node_id: str, address: str, port: int, capabilities: List[str]):
        """Add a new node to the network"""
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(
                id=node_id,
                address=address,
                port=port,
                status=NodeStatus.ACTIVE,
                last_seen=time.time(),
                version=1,
                capabilities=capabilities
            )
            self._log("NODE_DISCOVERED", {"node_id": node_id, "address": address})
    
    def send_message(self, msg_type: MessageType, recipient: Optional[str], 
                    payload: Dict) -> Message:
        """Send a message to a node or broadcast"""
        msg = Message(
            id=str(uuid.uuid4())[:8],
            msg_type=msg_type,
            sender=self.node_id,
            recipient=recipient,
            timestamp=datetime.utcnow().isoformat() + "Z",
            payload=payload,
            signature=self._sign(msg_type, payload)
        )
        
        self.message_log.append(msg)
        
        # Simulate message delivery
        if recipient:
            self._log("MESSAGE_SENT", {"to": recipient, "type": msg_type.value})
        else:
            self._log("BROADCAST", {"type": msg_type.value})
        
        return msg
    
    def _sign(self, msg_type: MessageType, payload: Dict) -> str:
        """Sign a message (simplified)"""
        content = f"{self.node_id}:{msg_type.value}:{json.dumps(payload, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def propose(self, proposal_id: str, value: Dict) -> bool:
        """Propose a value for consensus"""
        self.pending_proposals[proposal_id] = value
        self.votes[proposal_id] = set()
        
        # Broadcast proposal
        self.send_message(
            MessageType.PROPOSE,
            None,  # broadcast
            {"proposal_id": proposal_id, "value": value}
        )
        
        return True
    
    def vote(self, proposal_id: str) -> bool:
        """Vote on a proposal"""
        if proposal_id not in self.pending_proposals:
            return False
        
        self.votes[proposal_id].add(self.node_id)
        
        # Count votes
        quorum = len(self.nodes) // 2 + 1
        if len(self.votes[proposal_id]) >= quorum:
            return self.commit(proposal_id)
        
        return False
    
    def commit(self, proposal_id: str) -> bool:
        """Commit a proposal"""
        if proposal_id not in self.pending_proposals:
            return False
        
        self.committed.add(proposal_id)
        
        self.send_message(
            MessageType.COMMIT,
            None,
            {"proposal_id": proposal_id, "value": self.pending_proposals[proposal_id]}
        )
        
        del self.pending_proposals[proposal_id]
        
        self._log("COMMITTED", {"proposal_id": proposal_id})
        return True
    
    def sync_state(self) -> Dict:
        """Get current network state for sync"""
        return {
            "node_id": self.node_id,
            "peer_count": len(self.nodes) - 1,
            "committed_proposals": list(self.committed),
            "pending_proposals": list(self.pending_proposals.keys()),
            "message_count": len(self.message_log)
        }
    
    def run_heartbeat(self):
        """Simulate heartbeat to detect failures"""
        for node_id, node in self.nodes.items():
            if node_id == self.node_id:
                continue
            
            # Simulate failure detection
            if random.random() < 0.05:  # 5% chance of failure
                node.status = NodeStatus.FAILED
                self._log("NODE_FAILED", {"node_id": node_id})
            else:
                node.last_seen = time.time()
                node.status = NodeStatus.ACTIVE
    
    def _log(self, event_type: str, data: Dict):
        """Internal logging"""
        # In real implementation, would log to spine
        pass
    
    def get_topology(self) -> Dict:
        """Get network topology"""
        return {
            "node_id": self.node_id,
            "total_nodes": len(self.nodes),
            "active_nodes": sum(1 for n in self.nodes.values() if n.status == NodeStatus.ACTIVE),
            "nodes": {
                nid: {"status": n.status.value, "last_seen": n.last_seen, "capabilities": n.capabilities}
                for nid, n in self.nodes.items()
            },
            "committed": len(self.committed),
            "pending": len(self.pending_proposals)
        }


# Demo
if __name__ == "__main__":
    # Create network
    network = NetworkMesh("node-alpha", 9000)
    
    print("=== EVEZ Network Mesh ===\n")
    
    # Discover other nodes
    network.discover_node("node-beta", "192.168.1.10", 9001, ["spine", "finance"])
    network.discover_node("node-gamma", "192.168.1.11", 9002, ["cognition", "swarm"])
    network.discover_node("node-delta", "192.168.1.12", 9003, ["agent", "pattern"])
    
    print(f"Discovered {len(network.nodes) - 1} peers")
    
    # Propose and vote
    network.propose("prop-001", {"action": "update_thresholds", "value": {"local": 20.0}})
    network.vote("prop-001")
    network.vote("prop-001")  # Simulate another vote
    network.vote("prop-001")  # Simulate third vote
    
    print(f"Committed proposals: {network.committed}")
    
    # Run heartbeat
    network.run_heartbeat()
    
    print("\n=== Network Topology ===")
    print(json.dumps(network.get_topology(), indent=2))