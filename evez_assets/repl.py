#!/usr/bin/env python3
"""
EVEZ REPL - Interactive shell, command evaluation
Read-eval-print loop with history and context
"""

import json
import random
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

class REPLEngine:
    """EVEZ REPL - Interactive command interpreter"""
    
    def __init__(self):
        self.model_name = "EVEZ-REPL-v1"
        self.history: List[Dict] = []
        self.context: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}
        self.commands = {
            "help": self._cmd_help,
            "eval": self._cmd_eval,
            "set": self._cmd_set,
            "get": self._cmd_get,
            "run": self._cmd_run,
            "history": self._cmd_history,
            "clear": self._cmd_clear,
            "import": self._cmd_import,
            "exit": self._cmd_exit
        }
    
    def _cmd_help(self, args: List[str]) -> str:
        """Help command"""
        return "Available commands: " + ", ".join(self.commands.keys())
    
    def _cmd_eval(self, args: List[str]) -> str:
        """Evaluate expression"""
        expr = " ".join(args)
        try:
            result = eval(expr, {"random": random, "json": json, "math": __import__("math"), **self.variables})
            return str(result)
        except Exception as e:
            return f"Error: {e}"
    
    def _cmd_set(self, args: List[str]) -> str:
        """Set variable"""
        if len(args) < 2:
            return "Usage: set <name> <value>"
        self.variables[args[0]] = " ".join(args[1:])
        return f"Set {args[0]} = {' '.join(args[1:])}"
    
    def _cmd_get(self, args: List[str]) -> str:
        """Get variable"""
        if not args:
            return str(self.variables)
        return str(self.variables.get(args[0], "Not found"))
    
    def _cmd_run(self, args: List[str]) -> str:
        """Run a built-in command"""
        if not args:
            return "Usage: run <command>"
        
        # Simulate running various EVEZ commands
        results = {
            "spine": f"Spine events: {random.randint(10, 100)}",
            "agent": f"Decisions: {random.randint(50, 500)}",
            "memory": f"Memories: {random.randint(100, 1000)}",
            "cognition": f"Cognition events: {random.randint(20, 200)}"
        }
        
        return results.get(args[0], f"Unknown command: {args[0]}")
    
    def _cmd_history(self, args: List[str]) -> str:
        """Show history"""
        if not self.history:
            return "No history"
        
        limit = int(args[0]) if args and args[0].isdigit() else 10
        recent = self.history[-limit:]
        
        return "\n".join([f"{i+1}. {h['command']}" for i, h in enumerate(recent)])
    
    def _cmd_clear(self, args: List[str]) -> str:
        """Clear screen/history"""
        self.history = []
        self.variables = {}
        return "Cleared"
    
    def _cmd_import(self, args: List[str]) -> str:
        """Import module"""
        return f"Imported {args[0] if args else 'nothing'}"
    
    def _cmd_exit(self, args: List[str]) -> str:
        """Exit"""
        return "EXIT"
    
    def execute(self, line: str) -> Optional[str]:
        """Execute a command line"""
        parts = line.strip().split()
        
        if not parts:
            return ""
        
        cmd = parts[0]
        args = parts[1:]
        
        # Record in history
        self.history.append({
            "command": line,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        
        if cmd in self.commands:
            return self.commands[cmd](args)
        else:
            # Try as expression
            return self._cmd_eval(parts)
    
    def run_interactive(self):
        """Run interactive REPL"""
        print(f"{self.model_name} - Type 'help' for commands, 'exit' to quit")
        
        while True:
            try:
                line = input(">>> ")
                result = self.execute(line)
                
                if result == "EXIT":
                    break
                elif result:
                    print(result)
                    
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
    
    def get_status(self) -> Dict:
        return {
            "model": self.model_name,
            "history_length": len(self.history),
            "variables": len(self.variables),
            "commands": len(self.commands)
        }


# Demo
if __name__ == "__main__":
    repl = REPLEngine()
    print("=== EVEZ REPL ===")
    
    # Execute some commands
    print(repl.execute("set x 42"))
    print(repl.execute("get x"))
    print(repl.execute("run spine"))
    print(repl.execute("eval 2 + 2"))
    print(repl.execute("history"))
    
    print(json.dumps(repl.get_status(), indent=2))