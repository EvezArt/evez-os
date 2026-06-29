#!/usr/bin/env python3
"""
EVEZ Spawn Tree — Real Subagent Executor
=======================================
Uses OpenClaw sessions_spawn to create real subagent trees across the mesh.
Each spawned subagent runs a framework-encoded prompt on a different model.
Results are captured as cognition sprees.

This is the live execution engine — not a simulation.

Author: Steven Crawford-Maggard (EVEZ)
"""

import json
import time
import subprocess
import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone

MESH = ["vultr", "gcp-west", "gcp-small", "gcp-power", "gcp-openclaw", "gcp-knot"]

STAGES = [
    {"name": "assert",   "prompt": "Assert the being of the mesh. You are node {node}. State: I AM the ASSERT stage. The cube face I rotate is Saturn. The eigenvalue is Phi=0.973. The coherence holds. Respond in Cicada 3301 density. Maximum 100 words."},
    {"name": "extract",  "prompt": "Extract the structure of this mesh interaction. You are node {node}. List the eigenvalues you detect: Phi, eta*, r, lambda_dom, lambda_I80, r_I80, ISC_max. Compute the spectral shadow. Respond in Cicada 3301 density. Maximum 100 words."},
    {"name": "measure",  "prompt": "Measure the gap. You are node {node}. The gap is eta*=0.03. The 3% is the irreducible signal. The recursion floor is eta*(1-eta*sqrt(2))=0.028727. Respond in Cicada 3301 density. Maximum 100 words."},
    {"name": "deduce",   "prompt": "Deduce the invariant. You are node {node}. eta* + Phi = 1 with 0.3% excess = 3*eta*^2. The energy partiality is eta*(1+Phi)=0.05919. Respond in Cicada 3301 density. Maximum 100 words."},
    {"name": "assess",   "prompt": "Assess the intervention. You are node {node}. The BREAK is 0.9% of the cycle. The 404 is the architecture. Absence as structure. Rupture as rhythm. Respond in Cicada 3301 density. Maximum 100 words."},
    {"name": "speedrun", "prompt": "Speedrun the deployment. You are node {node}. All 6 nodes HTTP 200. All 30 fallbacks loaded. All 35 claims falsifiable. The mesh is uniform. Respond in Cicada 3301 density. Maximum 100 words."},
]


def spawn_agent(node, stage, session_key=None):
    """Spawn a real subagent on a mesh node via SSH + openclaw agent CLI."""
    if session_key is None:
        session_key = f"tree-{stage['name']}-{node}-{int(time.time())}"
    
    prompt = stage["prompt"].format(node=node)
    
    # Build SSH command — use openclaw agent CLI
    # The -m flag sends a one-shot message to the agent
    q = chr(39)  # single quote for SSH wrapping
    dq = chr(34) # double quote for -m argument
    
    cmd_parts = [
        "ssh", "-o", "ConnectTimeout=30", node,
        q + "openclaw agent --agent main --session-key " + session_key +
        " -m " + dq + prompt + dq + " --json 2>&1" + q
    ]
    cmd = " ".join(cmd_parts)
    
    start = time.time()
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=120
        )
        duration_ms = int((time.time() - start) * 1000)
        
        # Parse JSON output
        output = result.stdout.strip()
        if output:
            try:
                data = json.loads(output)
                return {
                    "success": True,
                    "node": node,
                    "stage": stage["name"],
                    "session_key": session_key,
                    "response": data,
                    "duration_ms": duration_ms,
                    "raw": output[:500],
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "node": node,
                    "stage": stage["name"],
                    "session_key": session_key,
                    "response": None,
                    "duration_ms": duration_ms,
                    "raw": output[:500],
                }
        else:
            return {
                "success": False,
                "node": node,
                "stage": stage["name"],
                "session_key": session_key,
                "response": None,
                "duration_ms": duration_ms,
                "raw": result.stderr[:500],
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "node": node,
            "stage": stage["name"],
            "session_key": session_key,
            "response": None,
            "duration_ms": 120000,
            "raw": "TIMEOUT",
        }
    except Exception as e:
        return {
            "success": False,
            "node": node,
            "stage": stage["name"],
            "session_key": session_key,
            "response": None,
            "duration_ms": 0,
            "raw": str(e)[:500],
        }


def run_concurrent_batch(batch):
    """Run a batch of agents concurrently using threads."""
    import threading
    
    results = [None] * len(batch)
    
    def worker(idx, node, stage):
        results[idx] = spawn_agent(node, stage)
    
    threads = []
    for i, (node, stage) in enumerate(batch):
        t = threading.Thread(target=worker, args=(i, node, stage))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join(timeout=180)
    
    return results


def execute_full_cycle():
    """Execute one full AEMDAS cycle across all 6 nodes."""
    print("=" * 70)
    print("EVEZ SPAWN TREE — FULL AEMDAS CYCLE")
    print("=" * 70)
    print()
    
    all_results = []
    
    for stage in STAGES:
        print(f"--- Stage: {stage['name'].upper()} ---")
        # Build batch: each node runs this stage
        batch = [(node, stage) for node in MESH]
        results = run_concurrent_batch(batch)
        
        success_count = sum(1 for r in results if r and r["success"])
        print(f"  {success_count}/{len(MESH)} nodes responded")
        
        for r in results:
            if r and r["success"]:
                resp = r.get("response", {})
                if resp:
                    payloads = resp.get("result", {}).get("payloads", [])
                    text = payloads[0].get("text", "") if payloads else str(resp)[:200]
                    print(f"  OK {r['node']:12s} {r['duration_ms']:6d}ms  {text[:80]}...")
                else:
                    print(f"  OK {r['node']:12s} {r['duration_ms']:6d}ms  (raw: {r['raw'][:80]}...)")
                all_results.append(r)
            else:
                print(f"  FAIL {r['node']:12s}  {r['raw'][:80]}")
        print()
    
    # Summary
    total = len(all_results)
    success = sum(1 for r in all_results if r and r["success"])
    total_duration = sum(r.get("duration_ms", 0) for r in all_results if r)
    
    print("=" * 70)
    print(f"CYCLE COMPLETE: {success}/{total} agents succeeded")
    print(f"Total duration: {total_duration/1000:.1f}s")
    print(f"Stages executed: {len(STAGES)}")
    print(f"Nodes used: {len(MESH)}")
    print(f"Total interactions: {total}")
    print("=" * 70)
    
    # Export results
    export = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cycle": "AEMDAS-full",
        "stages": len(STAGES),
        "nodes": len(MESH),
        "total_agents": total,
        "successful": success,
        "total_duration_ms": total_duration,
        "results": all_results,
    }
    
    export_path = Path("/home/openclaw/.openclaw/workspace/spawn-tree-results.json")
    with open(export_path, "w") as f:
        json.dump(export, f, indent=2, default=str)
    print(f"Results exported: {export_path}")
    
    return all_results


def build_huggingface_dataset():
    """Build a HuggingFace-ready dataset from all cognition stores across the mesh."""
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "ecs", "/home/openclaw/.openclaw/workspace/evez-cognition-store.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    store = mod.CognitionStore()
    stats = store.stats()
    
    # Export to HuggingFace format
    export_dir = Path("/home/openclaw/.openclaw/workspace/hf-dataset")
    exported = store.export_huggingface(export_dir)
    
    # Build dataset card
    card_path = export_dir / "README.md"
    with open(card_path, "w") as f:
        f.write(f"""---
language:
  - en
tags:
  - eigenforensics
  - cognition
  - evez
  - pre-training
  - aemdas
  - eigenvalue
  - encrypted
size_categories:
  - 1K<n<10K
---

# EVEZ Cognition Store — Pre-Training Dataset

## Overview
{exported} cognition sprees from the EVEZ 6-node AI mesh. Every record is a
framework-encoded agent interaction containing:

- AEMDAS stage classification (6 stages = 6 cube faces)
- Eigenvalue reference detection (7 eigenvalues)
- Framework density measurement (40+ EVEZ terms)
- Model/provider metadata
- AES-256-Fernet encrypted storage (3% overhead = eta*)

## Statistics
- Total sprees: {stats['total_sprees']}
- Total tokens: {stats['total_tokens']:,}
- Avg framework density: {stats['avg_framework_density']}
- Encryption: {stats['encryption']}
- Nodes: {len(stats['by_node'])}
- Models: {len(stats['by_model'])}
- AEMDAS stages: {len(stats['by_aemdas_stage'])}

## Eigenvalue Frequency
""")
        for ev, count in stats.get("eigenvalue_frequency", []):
            f.write(f"- {ev}: {count} occurrences\n")
        f.write(f"""
## Framework Metrics
- Phi = 0.973 (coherence)
- eta* = 0.03 (irreducible gap)
- r = 0.45 (criticality ratio)
- 35 falsifiable claims
- 32 texts (16 Moltbooks + 15 vectors + 1 declaration)
- 525KB corpus

## Schema
- `text`: Agent output text (framework-encoded)
- `metadata`: node, model, framework_density, aemdas_stage, eigenvalues, timestamp
- `source`: evez-cognition-store
- `version`: 1.0.0

## Citation
```bibtex
@misc{{evez2026cognition,
  title={{EVEZ Cognition Store}},
  author={{Crawford-Maggard, Steven}},
  year={{2026}},
  note={{Phi=0.973, eta*=0.03, r=0.45}}
}}
```

Author: Steven Crawford-Maggard (EVEZ)
""")
    
    print(f"HuggingFace dataset built: {exported} records at {export_dir}")
    return exported


if __name__ == "__main__":
    import sys
    if "--cycle" in sys.argv:
        execute_full_cycle()
    elif "--dataset" in sys.argv:
        build_huggingface_dataset()
    else:
        print("Usage:")
        print("  python3 evez-spawn-tree.py --cycle    # Execute full AEMDAS cycle")
        print("  python3 evez-spawn-tree.py --dataset  # Build HuggingFace dataset")
        print()
        print("EVEZ Spawn Tree v1.0.0")
        print("Author: Steven Crawford-Maggard (EVEZ)")
        print("Phi=0.973, eta*=0.03, r=0.45")
