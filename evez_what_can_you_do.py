#!/usr/bin/env python3
"""EVEZ Capability Query Interface

Usage:
  python3 evez_what_can_you_do.py                    # List all capabilities
  python3 evez_what_can_you_do.py search <query>     # Search capabilities
  python3 evez_what_can_you_do.py friction            # Show high-friction capabilities
  python3 evez_what_can_you_do.py blindspots          # Show hidden capabilities
  python3 evez_what_can_you_do.py chains              # Show capability chains
  python3 evez_what_can_you_do.py activate            # Auto-activate missing capabilities
  python3 evez_what_can_you_do.py graph               # Show capability graph
"""
import json, sys, re, subprocess
from pathlib import Path

W = Path("/home/openclaw/.openclaw/workspace")

def load_catalog():
    p = W / "capability-catalog.json"
    return json.load(open(p)) if p.exists() else {}

def load_graph():
    p = W / "capability-graph.json"
    return json.load(open(p)) if p.exists() else {}

def cmd_list():
    cat = load_catalog()
    caps = cat.get("capabilities", [])
    print(f"EVEZ Capability Catalog ({len(caps)} tools)")
    print("=" * 60)
    for c in caps:
        fname = c.get("file", "?")
        desc = c.get("description", "")[:60]
        if not desc:
            desc = ", ".join(c.get("functions", [])[:3])
        print(f"  {fname:<40} {desc}")
    print(f"\nTotal: {len(caps)} tools")

def cmd_search(query):
    cat = load_catalog()
    q = query.lower()
    results = []
    for c in cat.get("capabilities", []):
        text = (c.get("file", "") + " " + " ".join(c.get("functions", [])) + " " + c.get("description", "")).lower()
        if q in text:
            results.append(c)
    print(f"Search: {query} ({len(results)} results)")
    for r in results:
        fname = r.get("file", "?")
        desc = r.get("description", "?")[:80]
        print(f"  {fname}: {desc}")

def cmd_friction():
    cat = load_catalog()
    for f in sorted(cat.get("friction_map", []), key=lambda x: x.get("friction_score", 0), reverse=True):
        score = f.get("friction_score", 0)
        cap = f.get("capability", "?")
        reason = f.get("reason", "?")
        steps = f.get("steps", [])
        print(f"  [{score} stars] {cap}")
        print(f"    Steps: {len(steps)} - {reason}")

def cmd_blindspots():
    cat = load_catalog()
    for b in cat.get("blindspots", []):
        btype = b.get("type", "?")
        name = b.get("file", b.get("var", b.get("skill", "?")))
        print(f"  {btype}: {name}")

def cmd_chains():
    g = load_graph()
    for e in g.get("edges", []):
        src = e.get("source", "?")
        tgt = e.get("target", "?")
        etype = e.get("type", "?")
        if etype == "import":
            print(f"  {src} -> {tgt} (import)")
        elif etype == "shared_data":
            f = e.get("file", "?")
            print(f"  {src} <-> {tgt} (shared: {f})")

def cmd_graph():
    g = load_graph()
    nodes = g.get("nodes", [])
    edges = g.get("edges", [])
    print(f"Capability Graph: {len(nodes)} nodes, {len(edges)} edges")
    for n in nodes[:20]:
        print(f"  {n.get('name', '?')}: {n.get('size', 0)} bytes, {len(n.get('local_imports', []))} local imports")

def cmd_activate():
    print("Auto-activating capabilities...")
    r = subprocess.run([sys.executable, str(W / "evez_auto_activate.py")], capture_output=True, text=True)
    print(r.stdout)
    if r.stderr:
        print(f"Errors: {r.stderr[:200]}")

def main():
    if len(sys.argv) < 2:
        cmd_list()
        return
    cmd = sys.argv[1]
    if cmd == "search" and len(sys.argv) > 2:
        cmd_search(sys.argv[2])
    elif cmd == "friction":
        cmd_friction()
    elif cmd == "blindspots":
        cmd_blindspots()
    elif cmd == "chains":
        cmd_chains()
    elif cmd == "graph":
        cmd_graph()
    elif cmd == "activate":
        cmd_activate()
    else:
        print(f"Unknown: {cmd}. Try: list, search, friction, blindspots, chains, graph, activate")

if __name__ == "__main__":
    main()
