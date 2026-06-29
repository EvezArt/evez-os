#!/usr/bin/env python3
"""Friction reducer for: proactive_messaging"""
import subprocess, sys, json
from pathlib import Path

STEPS = ["enable telegram plugin", "set bot token", "configure channel", "set cron job", "write message template", "trigger send"]
FRICTION = 6
REASON = "6-step chain with no documentation path connecting the steps"

def main():
    cap_name = "proactive_messaging"
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
