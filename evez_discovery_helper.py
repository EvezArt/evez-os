#!/usr/bin/env python3
"""EVEZ Discovery Helper - search and find any capability in the system."""
import json, sys, re
from pathlib import Path

CATALOG = json.load(open(Path("/home/openclaw/.openclaw/workspace/capability-catalog.json")))

def search(query):
    """Search capabilities by keyword."""
    results = []
    q = query.lower()
    for cap in CATALOG["capabilities"]:
        searchable = (cap["file"] + " " + " ".join(cap["functions"]) + " " + cap.get("description", "")).lower()
        if q in searchable:
            results.append(cap)
    return results

def list_all():
    """List all discovered capabilities."""
    for cap in CATALOG["capabilities"]:
        desc = cap.get("description", "")[:80]
        print(f"  {cap[chr(39)+chr(39)]+chr(39)}file{chr(39)+chr(39)+chr(39)]} - {desc}")
    print(f"
Total: {len(CATALOG[chr(39)+chr(39)]capabilities{chr(39)+chr(39)+chr(39)])} capabilities")
    print(f"Blindspots: {len(CATALOG.get(chr(39)+chr(39)]blindspots{chr(39)+chr(39)+chr(39)], []))}")
    print(f"Friction items: {len(CATALOG.get(chr(39)+chr(39)]friction_map{chr(39)+chr(39)+chr(39)], []))}")

def show_friction():
    """Show capabilities with highest discovery friction."""
    for f in sorted(CATALOG.get("friction_map", []), key=lambda x: x.get("friction_score", 0), reverse=True):
        score = f.get("friction_score", 0)
        cap = f.get("capability", "?")
        reason = f.get("reason", "?")
        print(f"  [{score}] {cap}: {reason}")

def show_blindspots():
    """Show capabilities that are hidden or hard to discover."""
    for b in CATALOG.get("blindspots", []):
        print(f"  {b.get(chr(39)+chr(39)]type{chr(39)+chr(39)+chr(39)]}: {b.get(chr(39)+chr(39)]file{chr(39)+chr(39)+chr(39)] or b.get(chr(39)+chr(39)]var{chr(39)+chr(39)+chr(39)] or b.get(chr(39)+chr(39)]skill{chr(39)+chr(39)+chr(39)], chr(39)+chr(39)]?{chr(39)+chr(39)+chr(39)])}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 evez_discovery_helper.py [search|list|friction|blindspots] [query]")
        return
    cmd = sys.argv[1]
    if cmd == "search" and len(sys.argv) > 2:
        for r in search(sys.argv[2]):
            print(f"  {r[chr(39)+chr(39)]file{chr(39)+chr(39)+chr(39)]}: {r[chr(39)+chr(39)]functions{chr(39)+chr(39)+chr(39)][:3]}")
    elif cmd == "list":
        list_all()
    elif cmd == "friction":
        show_friction()
    elif cmd == "blindspots":
        show_blindspots()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
