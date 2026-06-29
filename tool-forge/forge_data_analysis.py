#!/usr/bin/env python3
import subprocess, sys
if "--install" in sys.argv:
    subprocess.run(["pip3", "install", "--break-system-packages", "pandas"])
elif "--verify" in sys.argv:
    try:
        __import__("pandas"); print("INSTALLED")
    except: print("MISSING")
