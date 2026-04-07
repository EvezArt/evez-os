#!/usr/bin/env python3
"""
EVEZ-OS Run All
Execute full system with optional seed
"""

import sys
import argparse
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.evez import EvezOS

def main():
    parser = argparse.ArgumentParser(description="EVEZ-OS Full Run")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--mode", choices=["normal", "spicy"], default="normal", help="Run mode")
    parser.add_argument("--steps", type=int, default=14, help="Play steps")
    
    args = parser.parse_args()
    
    print(f"🔥 EVEZ-OS RUNALL (seed={args.seed}, mode={args.mode})")
    print("=" * 50)
    
    evez = EvezOS()
    evez.init()
    result = evez.play(seed=args.seed, steps=args.steps)
    
    print("\n" + "=" * 50)
    print("📊 FINAL STATE:")
    evez.status()
    
    return result


if __name__ == "__main__":
    main()