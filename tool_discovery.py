#!/usr/bin/env python3
"""
Tool Discovery - Auto-detect available tools
"""
import json
import subprocess

class ToolDiscovery:
    def __init__(self):
        self.tools = []
        
    def discover_openclaw(self):
        """Discover OpenClaw tools"""
        result = subprocess.run(
            ["openclaw", "tools", "list"],
            capture_output=True, text=True, timeout=10
        )
        return {"tools": result.stdout.split(), "count": len(result.stdout)}
    
    def discover_mcporter(self):
        """Discover mcporter tools"""
        result = subprocess.run(
            ["mcporter", "tools", "list"],
            capture_output=True, text=True, timeout=10
        )
        return {"tools": result.stdout.split(), "count": len(result.stdout)}
    
    def all_tools(self):
        """Get all available tools"""
        oc = self.discover_openclaw()
        mc = self.discover_mcporter()
        return {"openclaw": oc, "mcporter": mc}

if __name__ == "__main__":
    t = ToolDiscovery()
    print(t.discover_openclaw())
