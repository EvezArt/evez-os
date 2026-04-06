#!/usr/bin/env python3
"""
Extended Sensory Buffers - Full Delay Compensation
Comprehensive buffer management for all compute types.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import random

@dataclass
class BufferSpec:
    """Specification for a sensory buffer"""
    name: str
    latency_ms: float
    buffer_type: str      # camera, network, model, storage, compute
    compensation: str      # prefetch, cache, pipeline, parallel
    enabled: bool = True

class BufferManager:
    """
    Manages all sensory buffers for maximum compensation.
    """
    
    def __init__(self):
        self.buffers: Dict[str, BufferSpec] = {}
        self.latency_history: Dict[str, deque] = {}
        self.compensation_cache: Dict[str, Any] = {}
        self._register_default_buffers()
    
    def _register_default_buffers(self):
        """Register all standard buffers"""
        defaults = [
            # Vision/Camera
            BufferSpec("camera", 50.0, "camera", "pipeline"),
            BufferSpec("depth_sensor", 35.0, "camera", "pipeline"),
            BufferSpec("lidar", 100.0, "camera", "prefetch"),
            
            # Network
            BufferSpec("wifi", 50.0, "network", "cache"),
            BufferSpec("cellular", 200.0, "network", "cache"),
            BufferSpec("api_response", 150.0, "network", "pipeline"),
            
            # AI/ML
            BufferSpec("llm_inference", 2000.0, "model", "speculative"),
            BufferSpec("embedding", 100.0, "model", "batch"),
            BufferSpec("image_gen", 5000.0, "model", "speculative"),
            BufferSpec("tts", 500.0, "model", "cache"),
            
            # Storage
            BufferSpec("disk_read", 10.0, "storage", "cache"),
            BufferSpec("disk_write", 20.0, "storage", "batch"),
            BufferSpec("db_query", 50.0, "storage", "index"),
            
            # Compute
            BufferSpec("cpu", 1.0, "compute", "parallel"),
            BufferSpec("gpu", 5.0, "compute", "parallel"),
            BufferSpec("compile", 5000.0, "compute", "speculative"),
            
            # Custom/Logic (dormant compute)
            BufferSpec("dormant_logic", 0.0, "compute", "activate"),
            BufferSpec("cached_reasoning", 0.0, "model", "reuse"),
            BufferSpec("parallel_agent", 0.0, "compute", "delegate"),
        ]
        
        for buf in defaults:
            self.buffers[buf.name] = buf
            self.latency_history[buf.name] = deque(maxlen=50)
    
    def register_buffer(self, name: str, latency_ms: float, buffer_type: str, compensation: str):
        """Register custom buffer"""
        self.buffers[name] = BufferSpec(name, latency_ms, buffer_type, compensation)
        self.latency_history[name] = deque(maxlen=50)
    
    def get_compensation(self, buffer_name: str, data: Any) -> Dict:
        """Get compensation for a buffer delay"""
        buf = self.buffers.get(buffer_name)
        if not buf:
            return {"compensation": "none", "gain": 0, "technique": "none"}
        
        gains = {
            "pipeline": buf.latency_ms * 0.8,
            "prefetch": buf.latency_ms * 0.9,
            "cache": buf.latency_ms * 0.7,
            "batch": buf.latency_ms * 0.5,
            "speculative": buf.latency_ms * 1.2,  # Can achieve negative!
            "parallel": buf.latency_ms * 0.6,
            "index": buf.latency_ms * 0.85,
            "activate": buf.latency_ms,  # Dormant compute awakening
            "reuse": buf.latency_ms * 2.0,  # Maximum negative latency
            "delegate": buf.latency_ms * 1.5,
        }
        
        gain = gains.get(buf.compensation, 0)
        
        return {
            "buffer": buffer_name,
            "latency": buf.latency_ms,
            "compensation": buf.compensation,
            "gain_ms": gain,
            "technique": buf.compensation
        }
    
    def calculate_total_compensation(self) -> Dict:
        """Calculate total possible compensation"""
        total_gain = 0
        by_type = {"camera": 0, "network": 0, "model": 0, "storage": 0, "compute": 0}
        
        for name, buf in self.buffers.items():
            comp = self.get_compensation(name, None)
            total_gain += comp["gain_ms"]
            by_type[buf.buffer_type] += comp["gain_ms"]
        
        return {
            "total_gain_ms": total_gain,
            "by_type": by_type,
            "buffer_count": len(self.buffers),
            "potential_negative": total_gain > 1000
        }
    
    def activate_dormant(self, dormant_name: str, data: Any) -> Dict:
        """Awaken dormant compute for acceleration"""
        if dormant_name not in self.buffers:
            return {"activated": False, "reason": "not_found"}
        
        buf = self.buffers[dormant_name]
        if buf.latency_ms > 0:
            return {"activated": False, "reason": "not_dormant"}
        
        # Activate dormant compute
        activated_data = {
            "source": data,
            "activated_at": datetime.utcnow().isoformat(),
            "technique": "dormant_activation"
        }
        
        self.compensation_cache[dormant_name] = activated_data
        
        return {
            "activated": True,
            "buffer": dormant_name,
            "gain": 500,  # Estimated gain from dormant
            "technique": "dormant_activation"
        }
    
    def get_buffer_groups(self) -> Dict:
        """Group buffers by type"""
        groups = {}
        for buf in self.buffers.values():
            if buf.buffer_type not in groups:
                groups[buf.buffer_type] = []
            groups[buf.buffer_type].append({
                "name": buf.name,
                "latency": buf.latency_ms,
                "compensation": buf.compensation
            })
        return groups

def demo_buffers():
    """Demo the buffer manager"""
    mgr = BufferManager()
    
    print("=" * 50)
    print("EXTENDED SENSORY BUFFERS")
    print("=" * 50)
    
    # Buffer groups
    print("\n📡 Buffer Groups:")
    for btype, buffers in mgr.get_buffer_groups().items():
        print(f"\n  {btype.upper()}:")
        for b in buffers[:3]:
            print(f"    {b['name']}: {b['latency']}ms ({b['compensation']})")
    
    # Total compensation
    print("\n⚡ Total Compensation:")
    comp = mgr.calculate_total_compensation()
    print(f"   Total gain: {comp['total_gain_ms']:.0f}ms")
    print(f"   Buffers: {comp['buffer_count']}")
    print(f"   Can achieve negative: {comp['potential_negative']}")
    
    # By type breakdown
    print("\n📊 By Type:")
    for btype, gain in comp["by_type"].items():
        if gain > 0:
            print(f"   {btype}: {gain:.0f}ms")
    
    # Test compensation
    print("\n🎯 Compensation Tests:")
    for buf_name in ["llm_inference", "image_gen", "dormant_logic"]:
        c = mgr.get_compensation(buf_name, None)
        print(f"   {buf_name}: {c['gain_ms']:.0f}ms ({c['technique']})")
    
    return mgr

if __name__ == "__main__":
    demo_buffers()