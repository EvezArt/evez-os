#!/usr/bin/env python3
"""
EVEZ Hot-Reload Module
Live code reloading without restart

Usage:
    from hot_reload import HotReloader
    loader = HotReloader('modules/')
    loader.watch()  # Start watching
    # Or reload once:
    loader.reload('trunk_manager')
"""

import importlib
import inspect
import time
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ModuleReloader(FileSystemEventHandler):
    """Hot-reload a specific module"""
    
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.module_name = self.module_path.stem
        self.last_modified = self.module_path.stat().st_mtime
        self.module = None
        
    def reload(self):
        """Reload the module"""
        try:
            # Import fresh
            import sys
            if self.module_name in sys.modules:
                # Clear old module
                del sys.modules[self.module_name]
                
            # Re-import
            spec = importlib.util.spec_from_file_location(
                self.module_name, 
                self.module_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[self.module_name] = module
            spec.loader.exec_module(module)
            
            self.last_modified = self.module_path.stat().st_mtime
            return {"status": "reloaded", "module": self.module_name}
            
        except Exception as e:
            return {"error": str(e), "module": self.module_name}
            
    def needs_reload(self):
        """Check if file changed"""
        if not self.module_path.exists():
            return False
        current_mtime = self.module_path.stat().st_mtime
        return current_mtime > self.last_modified


class HotReloader:
    """
    Watch a directory and auto-reload changed modules.
    Or reload specific modules on demand.
    """
    
    def __init__(self, modules_dir="modules"):
        self.modules_dir = Path(modules_dir)
        self.reloaders = {}
        self.observer = None
        
    def register(self, module_name):
        """Register a module for hot-reload"""
        module_path = self.modules_dir / f"{module_name}.py"
        if module_path.exists():
            self.reloaders[module_name] = ModuleReloader(module_path)
            return {"registered": module_name}
        return {"error": f"Module not found: {module_name}"}
        
    def reload(self, module_name):
        """Manually reload a module"""
        if module_name not in self.reloaders:
            self.register(module_name)
            
        if module_name in self.reloaders:
            return self.reloaders[module_name].reload()
            
        return {"error": f"Module not registered: {module_name}"}
        
    def reload_all(self):
        """Reload all registered modules"""
        results = {}
        for name, reloader in self.reloaders.items():
            results[name] = reloader.reload()
        return results
        
    def check_changes(self):
        """Check if any modules need reload"""
        needs_reload = []
        for name, reloader in self.reloaders.items():
            if reloader.needs_reload():
                needs_reload.append(name)
        return needs_reload
        
    def watch(self, callback=None):
        """
        Start watching for file changes (requires watchdog).
        Without watchdog, use check_changes() in a loop.
        """
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class Handler(FileSystemEventHandler):
                def __init__(cb_self, reloader):
                    self.reloader = reloader
                    super().__init__()
                    
                def on_modified(self, event):
                    if event.src_path.endswith('.py'):
                        self.reloader.reload()
                        if callback:
                            callback(event.src_path)
                            
            self.observer = Observer()
            handler = Handler(self)
            self.observer.schedule(handler, str(self.modules_dir), recursive=False)
            self.observer.start()
            
            return {"status": "watching", "modules": list(self.reloaders.keys())}
            
        except ImportError:
            return {"error": "watchdog not installed. Use check_changes() manually."}
            
    def stop(self):
        """Stop watching"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        return {"status": "stopped"}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Hot Reload")
    parser.add_argument("command", choices=["register", "reload", "check", "watch", "stop"])
    parser.add_argument("--module", "-m", help="Module name")
    parser.add_argument("--dir", default="modules", help="Modules directory")
    
    args = parser.parse_args()
    
    loader = HotReloader(args.dir)
    
    if args.command == "register":
        if not args.module:
            print("Error: --module required")
            return
        result = loader.register(args.module)
        print(result)
        
    elif args.command == "reload":
        if not args.module:
            print("Error: --module required")
            return
        result = loader.reload(args.module)
        print(result)
        
    elif args.command == "check":
        result = loader.check_changes()
        print({"needs_reload": result})
        
    elif args.command == "watch":
        result = loader.watch()
        print(result)
        
    elif args.command == "stop":
        result = loader.stop()
        print(result)


if __name__ == "__main__":
    main()