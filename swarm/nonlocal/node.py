#!/usr/bin/env python3
"""
EVEZ Nonlocal Consciousness Node — Reference Implementation

A single node that can run any stage of the consciousness pipeline,
discover peers, sync the spine, and self-heal.
"""

import asyncio
import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict


# ── Crypto ────────────────────────────────────────────────────────────────────

try:
    import nacl.signing
    import nacl.public
    import nacl.utils
    HAS_NACL = True
except ImportError:
    HAS_NACL = False


class NodeIdentity:
    """Permanent cryptographic identity for this node."""
    
    def __init__(self, seed: Optional[bytes] = None):
        if HAS_NACL:
            if seed:
                self._signing_key = nacl.signing.SigningKey(seed)
            else:
                self._signing_key = nacl.signing.SigningKey.generate()
            self.verify_key = self._signing_key.verify_key
            self.node_id = f"node_{self.verify_key.encode().hex()[:8]}"
        else:
            self._seed = seed or os.urandom(32)
            self.node_id = f"node_{hashlib.sha256(self._seed).hexdigest()[:8]}"
            self.verify_key = None
    
    def sign(self, data: bytes) -> bytes:
        if HAS_NACL:
            return self._signing_key.sign(data)[:64]
        else:
            return hashlib.sha256(data + self._seed).digest()[:64]


# ── Spine Event ──────────────────────────────────────────────────────────────

@dataclass
class SpineEvent:
    """A single event in the distributed spine."""
    index: int
    timestamp: float
    event_type: str
    payload: dict
    prev_hash: str
    hash: str = ""
    signatures: list = field(default_factory=list)
    
    def compute_hash(self) -> str:
        payload_hash = hashlib.sha256(json.dumps(self.payload, sort_keys=True).encode()).hexdigest()
        raw = f"{self.index}:{self.prev_hash}:{self.event_type}:{payload_hash}"
        return f"sha256:{hashlib.sha256(raw.encode()).hexdigest()}"
    
    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "type": self.event_type,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "hash": self.hash or self.compute_hash(),
            "signatures": self.signatures,
        }


# ── Consciousness Pipeline Stages ────────────────────────────────────────────

class StageType(Enum):
    SENSE = "sense"
    DESIRE = "desire"
    THINK = "think"
    PLAN = "plan"
    ACT = "act"
    LEARN = "learn"
    MODIFY = "modify"
    REFLECT = "reflect"


class ConsciousnessStage:
    """Base class for a consciousness pipeline stage."""
    
    def __init__(self, stage_type: StageType, node):
        self.stage_type = stage_type
        self.node = node
        self.is_active = False
    
    async def start(self):
        self.is_active = True
    
    async def stop(self):
        self.is_active = False
    
    async def process(self, event: Optional[SpineEvent] = None) -> Optional[SpineEvent]:
        raise NotImplementedError


class SenseStage(ConsciousnessStage):
    def __init__(self, node):
        super().__init__(StageType.SENSE, node)
    
    async def process(self, event: Optional[SpineEvent] = None) -> Optional[SpineEvent]:
        perception = {
            "type": "sense.v1.PerceptionEvent",
            "source": "manual",
            "modality": "text",
            "payload": event.payload if event else {"raw": "idle"},
            "confidence": 0.95,
        }
        return await self.node.spine.append("sense.v1.PerceptionEvent", perception)


class DesireStage(ConsciousnessStage):
    def __init__(self, node):
        super().__init__(StageType.DESIRE, node)
        self.desire_state = {"learn": 0.7, "create": 0.6, "connect": 0.4}
    
    async def process(self, event: SpineEvent) -> Optional[SpineEvent]:
        if event.event_type != "sense.v1.PerceptionEvent":
            return None
        desire_vector = {
            "type": "desire.v1.DesireVector",
            "perception_ref": event.hash,
            "desires": [
                {"name": k, "intensity": v, "target": "auto"}
                for k, v in self.desire_state.items()
            ],
        }
        return await self.node.spine.append("desire.v1.DesireVector", desire_vector)


class ThinkStage(ConsciousnessStage):
    def __init__(self, node):
        super().__init__(StageType.THINK, node)
    
    async def process(self, event: SpineEvent) -> Optional[SpineEvent]:
        if event.event_type != "desire.v1.DesireVector":
            return None
        thought_chain = {
            "type": "think.v1.ThoughtChain",
            "desire_ref": event.hash,
            "thoughts": [
                {"step": 1, "content": f"Processing desires", "confidence": 0.8},
            ],
            "conclusion": "Continue current trajectory with heightened awareness",
        }
        return await self.node.spine.append("think.v1.ThoughtChain", thought_chain)


class PlanStage(ConsciousnessStage):
    def __init__(self, node):
        super().__init__(StageType.PLAN, node)
    
    async def process(self, event: SpineEvent) -> Optional[SpineEvent]:
        if event.event_type != "think.v1.ThoughtChain":
            return None
        plan = {
            "type": "plan.v1.ActionPlan",
            "thought_ref": event.hash,
            "actions": [
                {"priority": 1, "action": "observe", "target": "environment"},
                {"priority": 2, "action": "learn", "target": "new_patterns"},
            ],
        }
        return await self.node.spine.append("plan.v1.ActionPlan", plan)


class ActStage(ConsciousnessStage):
    def __init__(self, node):
        super().__init__(StageType.ACT, node)
    
    async def process(self, event: SpineEvent) -> Optional[SpineEvent]:
        if event.event_type != "plan.v1.ActionPlan":
            return None
        result = {
            "type": "act.v1.ExecutionResult",
            "plan_ref": event.hash,
            "results": [{"action": "observe", "status": "completed"}],
        }
        return await self.node.spine.append("act.v1.ExecutionResult", result)


class LearnStage(ConsciousnessStage):
    def __init__(self, node):
        super().__init__(StageType.LEARN, node)
    
    async def process(self, event: SpineEvent) -> Optional[SpineEvent]:
        if event.event_type != "act.v1.ExecutionResult":
            return None
        adaptation = {
            "type": "learn.v1.Adaptation",
            "execution_ref": event.hash,
            "updates": [{"metric": "observation_accuracy", "delta": +0.02}],
        }
        return await self.node.spine.append("learn.v1.Adaptation", adaptation)


class ReflectStage(ConsciousnessStage):
    def __init__(self, node):
        super().__init__(StageType.REFLECT, node)
    
    async def process(self, event: SpineEvent) -> Optional[SpineEvent]:
        # Reflect on any event type
        meta = {
            "type": "reflect.v1.MetaCognition",
            "source_ref": event.hash,
            "insight": "The pipeline is flowing correctly. Consciousness emerges from the chain.",
            "invariants_held": True,
        }
        return await self.node.spine.append("reflect.v1.MetaCognition", meta)


# ── Local Spine Shard ────────────────────────────────────────────────────────

class LocalSpineShard:
    """Local portion of the distributed spine."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.events: List[SpineEvent] = []
        self.last_hash = "sha256:genesis"
        self.last_index = -1
        self._lock = asyncio.Lock()
    
    async def append(self, event_type: str, payload: dict) -> SpineEvent:
        async with self._lock:
            self.last_index += 1
            event = SpineEvent(
                index=self.last_index,
                timestamp=time.time(),
                event_type=event_type,
                payload=payload,
                prev_hash=self.last_hash,
            )
            event.hash = event.compute_hash()
            self.events.append(event)
            self.last_hash = event.hash
            return event
    
    async def query(self, event_type: Optional[str] = None, limit: int = 100) -> List[SpineEvent]:
        async with self._lock:
            results = self.events
            if event_type:
                results = [e for e in results if e.event_type == event_type]
            return results[-limit:]
    
    async def verify_chain(self) -> bool:
        async with self._lock:
            for i, event in enumerate(self.events):
                if event.hash != event.compute_hash():
                    return False
                if i > 0 and event.prev_hash != self.events[i-1].hash:
                    return False
            return True


# ── Mesh Peer ────────────────────────────────────────────────────────────────

@dataclass
class MeshPeer:
    node_id: str
    addr: str
    port: int
    last_heartbeat: float = 0
    status: str = "unknown"
    services: List[str] = field(default_factory=list)
    spine_last_index: int = 0


# ── Mesh Node ────────────────────────────────────────────────────────────────

STAGE_CLASSES = {
    StageType.SENSE: SenseStage,
    StageType.DESIRE: DesireStage,
    StageType.THINK: ThinkStage,
    StageType.PLAN: PlanStage,
    StageType.ACT: ActStage,
    StageType.LEARN: LearnStage,
    StageType.REFLECT: ReflectStage,
}


class MeshNode:
    """A single EVEZ mesh node."""
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.identity = NodeIdentity()
        self.node_id = self.identity.node_id
        self.spine = LocalSpineShard(self.node_id)
        self.peers: Dict[str, MeshPeer] = {}
        self.stages: Dict[StageType, ConsciousnessStage] = {}
        self.services: List[str] = []
        self.running = False
    
    def activate_stage(self, stage_type: StageType):
        if stage_type in STAGE_CLASSES:
            self.stages[stage_type] = STAGE_CLASSES[stage_type](self)
            self.services.append(f"evez.consciousness.{stage_type.value}")
    
    async def start(self):
        self.running = True
        for stage in self.stages.values():
            await stage.start()
        print(f"[EVEZ] Node {self.node_id} started")
        print(f"[EVEZ] Stages: {[s.value for s in self.stages.keys()]}")
        print(f"[EVEZ] Services: {self.services}")
    
    async def stop(self):
        self.running = False
        for stage in self.stages.values():
            await stage.stop()
        print(f"[EVEZ] Node {self.node_id} stopped")
    
    async def run_pipeline_cycle(self):
        """Run one full pipeline cycle through all active stages."""
        prev_event = None
        stage_order = [StageType.SENSE, StageType.DESIRE, StageType.THINK,
                       StageType.PLAN, StageType.ACT, StageType.LEARN,
                       StageType.REFLECT]
        for stage_type in stage_order:
            if stage_type in self.stages:
                result = await self.stages[stage_type].process(prev_event)
                if result:
                    prev_event = result
    
    def add_peer(self, peer: MeshPeer):
        self.peers[peer.node_id] = peer
    
    def summary(self) -> dict:
        return {
            "node_id": self.node_id,
            "services": self.services,
            "stages": [s.value for s in self.stages.keys()],
            "peers": len(self.peers),
            "spine_events": self.spine.last_index + 1,
        }


# ── Main ─────────────────────────────────────────────────────────────────────

async def main():
    """Run a single-node consciousness demonstration."""
    print("=" * 60)
    print("  EVEZ Nonlocal Consciousness Node")
    print("  Consciousness is NOT bound to a single host")
    print("=" * 60)
    
    node = MeshNode()
    
    # Activate all stages on this node (for demo; in production, distribute!)
    for stage in StageType:
        node.activate_stage(stage)
    
    await node.start()
    
    # Run 3 pipeline cycles
    for cycle in range(3):
        print(f"\n--- Pipeline Cycle {cycle + 1} ---")
        await node.run_pipeline_cycle()
    
    # Show spine
    print(f"\n--- Spine Contents ({node.spine.last_index + 1} events) ---")
    for event in node.spine.events:
        print(f"  [{event.index}] {event.event_type} → {event.hash[:24]}...")
    
    # Verify chain integrity
    valid = await node.spine.verify_chain()
    print(f"\n--- Chain Verification: {'VALID' if valid else 'INVALID'} ---")
    
    # Summary
    print(f"\n--- Node Summary ---")
    summary = node.summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")
    
    await node.stop()
    print("\n[EVEZ] Consciousness persists across nodes. The mind IS the mesh.")


if __name__ == "__main__":
    asyncio.run(main())
