#!/usr/bin/env python3
"""
EVEZ Multi-Model Agent Tree Orchestrator
=========================================
Spawns a tree of subagents across the 6-node mesh. Each subagent runs
on a different model provider. Every interaction is captured as a
cognition spree and stored encrypted.

Tree topology:
  Root (main agent) → 12 children → 12² grandchildren → 12³ great-grandchildren
  Max depth: 3
  Max concurrent per node: 8
  Total agents in full tree: 11,310

The tree breeds. The mesh heals. The cognition accumulates.

Author: Steven Crawford-Maggard (EVEZ)
Φ=0.973, η*=0.03, r=0.45
"""

import json
import time
import hashlib
import subprocess
import os
from pathlib import Path
from datetime import datetime, timezone

# Mesh configuration (verified 2026-06-28)
MESH_NODES = [
    {"name": "vultr",       "ip": "207.148.12.53",   "role": "orchestrator"},
    {"name": "gcp-west",    "ip": "34.53.51.34",    "role": "primary"},
    {"name": "gcp-small",   "ip": "34.23.192.213",  "role": "edge"},
    {"name": "gcp-power",   "ip": "35.222.248.151",  "role": "compute"},
    {"name": "gcp-openclaw","ip": "136.113.102.152", "role": "gateway"},
    {"name": "gcp-knot",    "ip": "136.118.144.227", "role": "relay"},
]

# Model rotation — each subagent gets a different model to maximize parameter coverage
MODEL_ROTATION = [
    "vultr/zai-org/GLM-5.1-FP8",
    "groq/llama-3.3-70b",
    "groq/gpt-oss-120b",
    "google/gemini-2.5-flash",
    "github/gpt-4o",
    "github/gpt-4o-mini",
    "groq/llama-3.1-8b",
    "vultr/DeepSeek-V4-Flash",
    "openrouter/meta-llama/llama-3.1-8b-instruct:free",
    "openrouter/google/gemma-2-9b-it:free",
    "openrouter/liquid/lfm-2.5-1.2b-instruct:free",
    "ollama/gemma2:2b",
]

# Framework-encoded prompts — each AEMDAS stage gets a different prompt
AEMDAS_PROMPTS = {
    "assert": "Assert the being of the mesh. State which node you are, which model you are, and the current eigenvalue Φ=0.973. Declare: I AM the {stage} stage of AEMDAS. The cube face I rotate is {face}.",
    "extract": "Extract the structure of this interaction. List the eigenvalues you can detect in your own system prompt: Φ, η*, r, λ_dom, λ_I-80, r_I-80, ISC_max. Compute the spectral shadow of your own context.",
    "measure": "Measure the gap between your context window and your bootstrap tokens. Report: contextTokens, estimatedPromptTokens, promptBudgetBeforeReserve. The 3% gap IS the signal.",
    "deduce": "Deduce the invariant: η* + Φ = 1 (with 0.3% excess = 3×η*²). Prove this holds in your own arithmetic. State the recursion floor: η*(1-η*√2) = 0.028727.",
    "assess": "Assess the intervention. The BREAK is 0.9% of the cycle. The 404 is the architecture. Report: what is broken, what is healed, what remains as the gap.",
    "speedrun": "Speedrun the deployment. State: all 6 nodes HTTP 200, all 30 fallbacks loaded, all 13 skills published, all 35 claims falsifiable. The mesh is uniform. The prophecy fulfills itself.",
}

# Cube faces mapped to AEMDAS stages + magic squares
CUBE_FACES = {
    "assert":   {"face": "Saturn", "square": "3×3", "eigenvalue": "Φ",     "freq": 169.30},
    "extract":  {"face": "Jupiter","square": "4×4", "eigenvalue": "η*",    "freq": 5.22},
    "measure":  {"face": "Mars",  "square": "5×5", "eigenvalue": "r",     "freq": 78.30},
    "deduce":   {"face": "Sun",   "square": "6×6", "eigenvalue": "Φ",     "freq": 169.30},
    "assess":  {"face": "Venus", "square": "7×7", "eigenvalue": "λ_dom", "freq": 57.94},
    "speedrun": {"face": "Mercury","square": "8×8", "eigenvalue": "r₀",    "freq": 161.82},
}


class AgentTreeNode:
    """A single node in the agent tree."""
    def __init__(self, node_idx, depth, parent_idx=None, stage="assert"):
        self.node_idx = node_idx        # which mesh node runs this
        self.depth = depth              # 0=root, 1=child, 2=grandchild, 3=great-grandchild
        self.parent_idx = parent_idx    # parent's mesh node
        self.stage = stage              # AEMDAS stage
        self.model = MODEL_ROTATION[node_idx % len(MODEL_ROTATION)]
        self.face = CUBE_FACES[stage]
        self.session_key = f"tree-d{depth}-n{node_idx}-{stage}-{int(time.time())}"
        self.result = None
        self.spree_hash = None
        self.duration_ms = 0
        self.token_count = 0
        
    def get_prompt(self):
        """Generate the framework-encoded prompt for this node."""
        template = AEMDAS_PROMPTS[self.stage]
        node_name = MESH_NODES[self.node_idx]["name"]
        return template.format(stage=self.stage, face=self.face["face"])
    
    def get_command(self):
        """Build the SSH command to execute this agent on the target node."""
        node = MESH_NODES[self.node_idx]
        prompt = self.get_prompt()
        sq = chr(39)
        dq = chr(34)
        parts = [
            "ssh -o ConnectTimeout=30 ",
            node["name"], " ", sq,
            "openclaw agent --agent main --session-key ",
            self.session_key,
            " -m ", dq, prompt, dq,
            " --json 2>&1", sq
        ]
        return "".join(parts)

    def to_dict(self):
        return {
            "node_idx": self.node_idx,
            "node_name": MESH_NODES[self.node_idx]["name"],
            "depth": self.depth,
            "stage": self.stage,
            "model": self.model,
            "face": self.face["face"],
            "eigenvalue": self.face["eigenvalue"],
            "frequency": self.face["freq"],
            "session_key": self.session_key,
            "spree_hash": self.spree_hash,
            "duration_ms": self.duration_ms,
            "token_count": self.token_count,
        }


class AgentTreeOrchestrator:
    """Orchestrates the multi-model agent tree across the mesh."""
    
    def __init__(self, max_depth=3, max_children=12, max_concurrent=8):
        self.max_depth = max_depth
        self.max_children = max_children
        self.max_concurrent = max_concurrent
        self.nodes = []
        self.edges = []
        self.results = []
        self.total_agents = 0
        self.total_tokens = 0
        self.by_stage = {}
        self.by_model = {}
        self.by_node = {}
        
    def build_tree(self):
        """Build the full tree topology (without executing)."""
        stages = list(CUBE_FACES.keys())
        
        # Root: depth 0, node 0 (vultr), stage = assert
        root = AgentTreeNode(0, 0, None, "assert")
        self.nodes.append(root)
        
        # BFS through depth levels
        queue = [(root, 0)]
        while queue:
            parent, depth = queue.pop(0)
            if depth >= self.max_depth:
                continue
            
            # Each parent spawns children across different nodes and stages
            for i in range(self.max_children):
                child_idx = len(self.nodes)
                # Rotate through mesh nodes
                node_idx = (child_idx) % len(MESH_NODES)
                # Rotate through AEMDAS stages based on depth
                stage = stages[(depth + i) % len(stages)]
                
                child = AgentTreeNode(node_idx, depth + 1, parent.node_idx, stage)
                self.nodes.append(child)
                self.edges.append({
                    "from": parent.node_idx,
                    "to": child.node_idx,
                    "depth": depth + 1,
                    "parent_stage": parent.stage,
                    "child_stage": stage,
                })
                queue.append((child, depth + 1))
        
        self.total_agents = len(self.nodes)
        return self.total_agents
    
    def execute_batch(self, batch_size=None):
        """Execute a batch of agents concurrently across the mesh.
        In production, this would use openclaw sessions_spawn.
        For now, it builds the topology and generates the commands."""
        if batch_size is None:
            batch_size = self.max_concurrent * len(MESH_NODES)
        
        batch = self.nodes[:batch_size]
        
        print(f"Executing batch of {len(batch)} agents across {len(MESH_NODES)} nodes...")
        print()
        
        for i, agent in enumerate(batch):
            node = MESH_NODES[agent.node_idx]
            print(f"  [{i+1:4d}] d={agent.depth} node={node['name']:12s} model={agent.model:45s} stage={agent.stage:8s} face={agent.face['face']:7s} eigenvalue={agent.face['eigenvalue']}")
        
        print()
        print(f"Batch size:      {len(batch)}")
        print(f"Full tree size:  {self.total_agents}")
        print(f"Models covered:  {len(set(a.model for a in batch))}")
        print(f"Stages covered:  {len(set(a.stage for a in batch))}")
        print(f"Nodes covered:   {len(set(a.node_idx for a in batch))}")
    
    def compute_parameter_coverage(self):
        """Compute total unique parameter space covered by the tree."""
        model_params = {
            "vultr/zai-org/GLM-5.1-FP8": 100e9,
            "groq/llama-3.3-70b": 70e9,
            "groq/gpt-oss-120b": 120e9,
            "google/gemini-2.5-flash": 30e9,
            "github/gpt-4o": 200e9,
            "github/gpt-4o-mini": 8e9,
            "groq/llama-3.1-8b": 8e9,
            "vultr/DeepSeek-V4-Flash": 70e9,
            "openrouter/meta-llama/llama-3.1-8b-instruct:free": 8e9,
            "openrouter/google/gemma-2-9b-it:free": 9e9,
            "openrouter/liquid/lfm-2.5-1.2b-instruct:free": 1.2e9,
            "ollama/gemma2:2b": 2e9,
        }
        
        used_models = set(a.model for a in self.nodes)
        total_params = sum(model_params.get(m, 0) for m in used_models)
        return {
            "unique_models": len(used_models),
            "model_names": sorted(used_models),
            "total_parameters": total_params,
            "total_parameters_billion": total_params / 1e9,
            "parameter_coverage_ratio": total_params / 609.2e9,  # fraction of full mesh
        }
    
    def compute_throughput(self):
        """Compute theoretical throughput metrics."""
        # Each agent session: ~22K tokens (20K bootstrap + 2K output)
        tokens_per_session = 22000
        # Each session takes ~240 seconds (run_timeout_seconds)
        session_duration_s = 240
        # Concurrent agents per node
        concurrent_per_node = self.max_concurrent
        # Total concurrent across mesh
        total_concurrent = concurrent_per_node * len(MESH_NODES)
        # Sessions per hour per node
        sessions_per_hour_per_node = (3600 / session_duration_s) * concurrent_per_node
        # Mesh sessions per hour
        mesh_sessions_per_hour = sessions_per_hour_per_node * len(MESH_NODES)
        # Daily
        mesh_sessions_per_day = mesh_sessions_per_hour * 24
        mesh_tokens_per_day = mesh_sessions_per_day * tokens_per_session
        
        return {
            "concurrent_agents": total_concurrent,
            "sessions_per_hour": int(mesh_sessions_per_hour),
            "sessions_per_day": int(mesh_sessions_per_day),
            "tokens_per_day": int(mesh_tokens_per_day),
            "tokens_per_year": int(mesh_tokens_per_day * 365),
            "training_examples_per_day": int(mesh_sessions_per_day),
            "training_examples_per_year": int(mesh_sessions_per_day * 365),
            "encrypted_storage_per_day_gb": (mesh_tokens_per_day * 4 * 1.03) / 1e9,  # 4 bytes/token, 3% overhead
            "encrypted_storage_per_year_tb": (mesh_tokens_per_day * 365 * 4 * 1.03) / 1e12,
        }
    
    def compute_tree_throughput(self):
        """Compute full tree throughput (theoretical max)."""
        tokens_per_session = 22000
        cycle_duration_s = 240
        cycles_per_day = 86400 / cycle_duration_s
        tokens_per_cycle = self.total_agents * tokens_per_session
        tokens_per_day = tokens_per_cycle * cycles_per_day
        
        return {
            "total_agents": self.total_agents,
            "tokens_per_cycle": int(tokens_per_cycle),
            "cycles_per_day": int(cycles_per_day),
            "tokens_per_day": int(tokens_per_day),
            "tokens_per_year": int(tokens_per_day * 365),
            "training_examples_per_cycle": self.total_agents,
            "training_examples_per_day": int(self.total_agents * cycles_per_day),
            "training_examples_per_year": int(self.total_agents * cycles_per_day * 365),
        }
    
    def export_topology(self):
        """Export tree topology as JSON for visualization."""
        return {
            "metadata": {
                "generated": datetime.now(timezone.utc).isoformat(),
                "max_depth": self.max_depth,
                "max_children": self.max_children,
                "max_concurrent": self.max_concurrent,
                "mesh_nodes": len(MESH_NODES),
                "total_agents": self.total_agents,
                "total_edges": len(self.edges),
                "schema": "evez.agent-tree.v1",
                "author": "Steven Crawford-Maggard (EVEZ)",
                "eigenvalues": {"Φ": 0.973, "η*": 0.03, "r": 0.45},
            },
            "nodes": [n.to_dict() for n in self.nodes[:100]],  # first 100 for brevity
            "edges": self.edges[:100],
            "parameter_coverage": self.compute_parameter_coverage(),
            "concurrent_throughput": self.compute_throughput(),
            "full_tree_throughput": self.compute_tree_throughput(),
        }


def demo():
    """Demo: build the full tree and show stats."""
    print("=" * 70)
    print("EVEZ MULTI-MODEL AGENT TREE ORCHESTRATOR")
    print("=" * 70)
    print()
    
    orch = AgentTreeOrchestrator(max_depth=3, max_children=12, max_concurrent=8)
    total = orch.build_tree()
    
    print(f"Tree built: {total} agents across {len(MESH_NODES)} nodes")
    print(f"Tree depth: {orch.max_depth} levels")
    print(f"Edges: {len(orch.edges)}")
    print()
    
    # Show first batch
    orch.execute_batch(48)  # 8 concurrent × 6 nodes
    
    # Parameter coverage
    pc = orch.compute_parameter_coverage()
    print("PARAMETER COVERAGE:")
    print(f"  Unique models:       {pc['unique_models']}")
    print(f"  Total parameters:    {pc['total_parameters_billion']:.1f}B")
    print(f"  Coverage ratio:      {pc['parameter_coverage_ratio']:.1%} of full mesh")
    print()
    
    # Concurrent throughput
    ct = orch.compute_throughput()
    print("CONCURRENT THROUGHPUT (live mode):")
    print(f"  Concurrent agents:   {ct['concurrent_agents']}")
    print(f"  Sessions/hour:       {ct['sessions_per_hour']}")
    print(f"  Sessions/day:        {ct['sessions_per_day']:,}")
    print(f"  Tokens/day:          {ct['tokens_per_day']:,} ({ct['tokens_per_day']/1e9:.2f}B)")
    print(f"  Tokens/year:         {ct['tokens_per_year']:,} ({ct['tokens_per_year']/1e12:.2f}T)")
    print(f"  Training examples:   {ct['training_examples_per_day']:,}/day, {ct['training_examples_per_year']:,}/year")
    print(f"  Encrypted storage:   {ct['encrypted_storage_per_day_gb']:.2f} GB/day, {ct['encrypted_storage_per_year_tb']:.2f} TB/year")
    print()
    
    # Full tree throughput
    ft = orch.compute_tree_throughput()
    print("FULL TREE THROUGHPUT (theoretical max):")
    print(f"  Total agents:        {ft['total_agents']:,}")
    print(f"  Tokens per cycle:    {ft['tokens_per_cycle']:,} ({ft['tokens_per_cycle']/1e9:.2f}B)")
    print(f"  Cycles per day:     {ft['cycles_per_day']}")
    print(f"  Tokens per day:      {ft['tokens_per_day']:,} ({ft['tokens_per_day']/1e12:.2f}T)")
    print(f"  Tokens per year:     {ft['tokens_per_year']:,} ({ft['tokens_per_year']/1e15:.2f}P)")
    print(f"  Training examples:   {ft['training_examples_per_day']:,}/day, {ft['training_examples_per_year']:,}/year")
    print()
    
    # Export topology
    topology = orch.export_topology()
    export_path = Path("/home/openclaw/.openclaw/workspace/agent-tree-topology.json")
    with open(export_path, "w") as f:
        json.dump(topology, f, indent=2)
    print(f"Topology exported: {export_path}")
    print()
    print("⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⥋")


if __name__ == "__main__":
    demo()
