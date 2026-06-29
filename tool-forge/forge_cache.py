#!/usr/bin/env python3
import subprocess, sys
if "--install" in sys.argv:
    subprocess.run(["pip3", "install", "--break-system-packages", "redis"])
elif "--verify" in sys.argv:
    try:
        __import__("redis"); print("INSTALLED")
    except: print("MISSING")
