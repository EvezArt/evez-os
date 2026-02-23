#!/usr/bin/env python3
# EVEZ-OS MasterBus v1.0
# Orchestrates SpawnBus -> CapabilityBus -> ValidatorBus -> MetaBus
# Each bus reads outputs of prior buses. All 4 watch each other.
import json, os, importlib.util
from datetime import datetime, timezone

CELL = "/cells/599dc7f9-0b2b-4460-b917-5104fcbb91ef/workspace"
LOG_FILE = CELL + "/master_bus_log.jsonl"

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def emit_log(event_type, data):
    entry = {"ts": datetime.now(timezone.utc).isoformat(),
             "bus": "MasterBus", "event": event_type, **data}
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def run():
    print("=" * 60)
    print("MasterBus START -- " + datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M UTC"))
    print("=" * 60)
    emit_log("RUN_START", {"ts_start": datetime.now(timezone.utc).isoformat()})
    results = {}
    for bus_name, module_file in [("spawn", "spawn_bus"), ("capability", "capability_bus"),
                                   ("validator", "validator_bus"), ("meta", "meta_bus")]:
        print("\n[" + bus_name + "] Running...")
        try:
            mod = load_module(module_file, CELL + "/" + module_file + ".py")
            result = mod.run()
            results[bus_name] = result.get("health", "OK") if isinstance(result, dict) else "OK"
        except Exception as e:
            print("  ERROR: " + str(e))
            results[bus_name] = "ERROR: " + str(e)
            emit_log("BUS_ERROR", {"bus": bus_name, "error": str(e)})
    print("\n" + "=" * 60)
    status = "OK" if all("ERROR" not in str(v) for v in results.values()) else "PARTIAL"
    print("MasterBus END -- status=" + status)
    emit_log("RUN_END", {"status": status, "results": {k: str(v)[:80] for k, v in results.items()}})
    print("=" * 60)
    return results

if __name__ == "__main__":
    run()
