#!/usr/bin/env python3
"""Friction reducer for: quantum_computing"""
import subprocess, sys, json
from pathlib import Path

STEPS = ["install qiskit", "install qutip", "install pennylane", "find quantum-agents/ dir", "run qc_runner.py"]
FRICTION = 5
REASON = "Exists in workspace but no top-level entry point or menu"

def main():
    cap_name = "quantum_computing"
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
