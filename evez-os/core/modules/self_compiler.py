#!/usr/bin/env python3
"""
EVEZ Self-Compiler
Compiles and validates EVEZ-OS modules from source

Usage:
    from self_compiler import SelfCompiler
    compiler = SelfCompiler('core/')
    result = compiler.compile_all()
"""

import ast
import os
import sys
import json
from pathlib import Path
from datetime import datetime

class ModuleValidator:
    """Validate a single Python module"""
    
    def __init__(self, module_path):
        self.path = Path(module_path)
        self.errors = []
        self.warnings = []
        
    def validate(self):
        """Run all validation checks"""
        if not self.path.exists():
            return {"valid": False, "error": "File not found"}
            
        # Syntax check
        try:
            with open(self.path) as f:
                source = f.read()
            ast.parse(source)
        except SyntaxError as e:
            self.errors.append(f"Syntax error: {e}")
            
        # Import check
        try:
            with open(self.path) as f:
                source = f.read()
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._check_import(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._check_import(node.module)
                        
        except Exception as e:
            self.warnings.append(f"Import check failed: {e}")
            
        return {
            "valid": len(self.errors) == 0,
            "path": str(self.path),
            "errors": self.errors,
            "warnings": self.warnings
        }
        
    def _check_import(self, module_name):
        """Check if import is available"""
        if module_name.startswith('.'):
            return  # Relative import, skip
        try:
            __import__(module_name)
        except ImportError:
            self.warnings.append(f"Optional import not available: {module_name}")


class SelfCompiler:
    """
    Compiles EVEZ-OS modules and validates entire system.
    Part of the self-building OS: deployment that builds while running.
    """
    
    def __init__(self, core_dir="core"):
        self.core_dir = Path(core_dir)
        self.modules_dir = self.core_dir / "modules"
        self.results = {}
        self.compilation_log = []
        
    def compile_module(self, module_name):
        """Compile a single module (validate + bundle)"""
        module_path = self.modules_dir / f"{module_name}.py"
        
        validator = ModuleValidator(module_path)
        result = validator.validate()
        
        self.results[module_name] = result
        self._log(f"compiled: {module_name}", result["valid"])
        
        return result
        
    def compile_all(self):
        """Compile all modules in modules directory"""
        if not self.modules_dir.exists():
            return {"error": f"Modules dir not found: {self.modules_dir}"}
            
        for py_file in self.modules_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            module_name = py_file.stem
            self.compile_module(module_name)
            
        # Summary
        total = len(self.results)
        valid = sum(1 for r in self.results.values() if r.get("valid", False))
        
        return {
            "total_modules": total,
            "valid": valid,
            "failed": total - valid,
            "results": self.results
        }
        
    def build_manifest(self):
        """Build manifest of all modules (for self-hosting)"""
        manifest = {
            "version": "0.2.0",
            "compiled_at": datetime.utcnow().isoformat(),
            "modules": {}
        }
        
        if not self.modules_dir.exists():
            return {"error": "Modules dir not found"}
            
        for py_file in self.modules_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
                
            module_name = py_file.stem
            stat = py_file.stat()
            
            manifest["modules"][module_name] = {
                "path": str(py_file),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "valid": self.results.get(module_name, {}).get("valid", False)
            }
            
        return manifest
        
    def _log(self, event, success):
        """Log compilation event"""
        entry = {
            "event": event,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.compilation_log.append(entry)
        
    def get_log(self):
        """Get compilation log"""
        return self.compilation_log


def main():
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Self-Compiler")
    parser.add_argument("command", choices=["compile", "all", "manifest", "validate"])
    parser.add_argument("--module", "-m", help="Module name")
    parser.add_argument("--dir", default="core", help="Core directory")
    
    args = parser.parse_args()
    
    compiler = SelfCompiler(args.dir)
    
    if args.command == "compile":
        if not args.module:
            print("Error: --module required")
            return
        result = compiler.compile_module(args.module)
        print(json.dumps(result, indent=2))
        
    elif args.command == "all":
        result = compiler.compile_all()
        print(json.dumps(result, indent=2))
        
    elif args.command == "manifest":
        result = compiler.build_manifest()
        print(json.dumps(result, indent=2))
        
    elif args.command == "validate":
        result = compiler.compile_all()
        valid = result.get("valid", 0)
        total = result.get("total_modules", 0)
        print(f"VALIDATED: {valid}/{total} modules")
        if valid == total:
            print("✅ System ready for deployment")
        else:
            print(f"⚠️  {total - valid} modules have issues")


if __name__ == "__main__":
    main()