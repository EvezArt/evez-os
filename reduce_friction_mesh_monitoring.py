#!/usr/bin/env python3
"""Friction reducer for: mesh_monitoring"""
import subprocess, sys, json
from pathlib import Path

STEPS = ["know mesh IPs", "find health endpoint", "parse JSON", "set up cron", "configure alerting"]
FRICTION = 5
REASON = "IPs are in MEMORY.md, endpoints in HEARTBEAT.md, but no single discovery path"

def main():
    cap_name = "mesh_monitoring"
    print(f"Reducing friction for: {cap_name}")
    print(f"Current friction score: {FRICTION}")
    print(f"Reason: {REASON}")
    print()
    for i, step in enumerate(STEPS, 1):
        print(f"  Step {i}/{len(STEPS)}: {step}")
    print()
    print("To reduce this friction:")
    print("  1. Bundle these steps into a single command")
    print("  2. Document the full chain in one place")
    print("  3. Add to capability catalog with searchable keywords")

if __name__ == "__main__":
    main()
