#!/usr/bin/env python3
"""Auto-activate missing capabilities."""
import subprocess, sys, importlib
W = sys.path.insert(0, "/home/openclaw/.openclaw/workspace")

def install(pkg, desc):
    try: importlib.import_module(pkg); return f"Already installed: {pkg}"
    except ImportError: pass
    try:
        r = subprocess.run(["pip3", "install", "--break-system-packages", pkg], capture_output=True, text=True, timeout=120)
        return f"Installed: {pkg} ({desc})" if r.returncode == 0 else f"Failed: {pkg}"
    except Exception as e: return f"Error: {pkg}: {e}"

def enable_plugin(name):
    try:
        r = subprocess.run(["openclaw", "plugins", "enable", name], capture_output=True, text=True, timeout=10)
        return f"Enabled: {name}" if r.returncode == 0 else f"Skip: {name}"
    except: return f"Error: {name}"

def main():
    for pkg, desc in [("pandas", "data analysis"), ("docker", "containers"), ("redis", "cache"), ("aiohttp", "async HTTP")]:
        print(install(pkg, desc))
    for p in ["duckduckgo", "active-memory", "memory-wiki"]:
        print(enable_plugin(p))

if __name__ == "__main__": main()
