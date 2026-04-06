#!/usr/bin/env python3
"""
EVEZ Execution Engine
Multi-surface task execution with automatic routing
"""

import json
import subprocess
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

class ExecutionEngine:
    """
    Routes tasks to appropriate execution surfaces:
    - Local (subprocess)
    - HTTP API (requests)
    - OpenClaw (messaging)
    - GitHub (API)
    """
    
    def __init__(self, config_path=None):
        self.config = {
            "local_enabled": True,
            "http_enabled": True,
            "openclaw_enabled": True,
            "github_enabled": True,
            "default_timeout": 30
        }
        self.execution_log = []
        
    def execute(self, task):
        """
        Execute a task. Task format:
        {
            "surface": "local|http|openclaw|github",
            "command": "...",
            "url": "...",  # for http
            "method": "GET|POST",
            "body": {},
            "timeout": 30
        }
        """
        surface = task.get("surface", "local")
        start = datetime.utcnow()
        
        try:
            if surface == "local":
                result = self._execute_local(task)
            elif surface == "http":
                result = self._execute_http(task)
            elif surface == "openclaw":
                result = self._execute_openclaw(task)
            elif surface == "github":
                result = self._execute_github(task)
            else:
                result = {"error": f"Unknown surface: {surface}"}
                
        except Exception as e:
            result = {"error": str(e)}
            
        end = datetime.utcnow()
        
        # Log execution
        log_entry = {
            "task": task,
            "surface": surface,
            "result": result,
            "start": start.isoformat(),
            "duration_ms": int((end - start).total_seconds() * 1000)
        }
        self.execution_log.append(log_entry)
        
        return result
        
    def _execute_local(self, task):
        """Execute local command"""
        cmd = task.get("command", "")
        timeout = task.get("timeout", self.config["default_timeout"])
        
        result = subprocess.run(
            cmd, shell=True, capture_output=True, timeout=timeout,
            text=True
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
        
    def _execute_http(self, task):
        """Execute HTTP request"""
        import urllib.request
        import urllib.error
        
        url = task.get("url", "")
        method = task.get("method", "GET")
        body = task.get("body", {})
        timeout = task.get("timeout", self.config["default_timeout"])
        
        try:
            if method == "GET":
                req = urllib.request.Request(url)
            else:
                req = urllib.request.Request(url, data=json.dumps(body).encode(), 
                                             headers={'Content-Type': 'application/json'})
                req.get_method = lambda: method
            
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return {
                    "status_code": resp.status,
                    "body": resp.read().decode()[:1000],
                    "headers": dict(resp.headers)
                }
        except urllib.error.HTTPError as e:
            return {"error": str(e), "status_code": e.code}
        except Exception as e:
            return {"error": str(e)}
        
    def _execute_openclaw(self, task):
        """Execute via OpenClaw messaging (placeholder)"""
        # In real implementation, would use message tool
        return {
            "status": "openclaw_execution_not_implemented",
            "note": "Would send message via OpenClaw"
        }
        
    def _execute_github(self, task):
        """Execute GitHub API call"""
        import os
        import urllib.request
        import urllib.error
        
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return {"error": "GITHUB_TOKEN not set"}
            
        url = task.get("url", "")
        method = task.get("method", "GET")
        body = task.get("body", {})
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            if method == "GET":
                req = urllib.request.Request(url, headers=headers)
            else:
                req = urllib.request.Request(url, data=json.dumps(body).encode(), 
                                             headers={**headers, 'Content-Type': 'application/json'})
                req.get_method = lambda: method
                
            with urllib.request.urlopen(req) as resp:
                return {
                    "status_code": resp.status,
                    "body": resp.read().decode()[:1000]
                }
        except urllib.error.HTTPError as e:
            return {"error": str(e), "status_code": e.code}
        
    def get_log(self, limit=10):
        """Get recent execution log"""
        return self.execution_log[-limit:]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Execution Engine")
    parser.add_argument("command", choices=["run", "log"])
    parser.add_argument("--surface", default="local")
    parser.add_argument("--cmd", help="Command for local")
    parser.add_argument("--url", help="URL for http")
    parser.add_argument("--body", help="JSON body for POST")
    
    args = parser.parse_args()
    
    engine = ExecutionEngine()
    
    if args.command == "run":
        task = {"surface": args.surface}
        if args.cmd:
            task["command"] = args.cmd
        if args.url:
            task["url"] = args.url
        if args.body:
            task["body"] = json.loads(args.body)
            task["method"] = "POST"
            
        result = engine.execute(task)
        print(json.dumps(result, indent=2))
        
    elif args.command == "log":
        print(json.dumps(engine.get_log(), indent=2))


if __name__ == "__main__":
    main()