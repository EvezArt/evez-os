"""Command-line self-audit demo."""
from __future__ import annotations
import argparse
import json
import tempfile
from .invariants import authorization_battery
from .runtime import EvidenceRuntime
from .spine import EvidenceSpine
from .surface import SurfaceMapper
from .self_audit import SelfAuditor

def run_demo() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        spine = EvidenceSpine(f"{tmp}/chain.jsonl")
        result = EvidenceRuntime(spine=spine).run(
            run_id="self-audit-authority-conflict",
            claim="Tool authorization cannot be bypassed.",
            surface=SurfaceMapper().default_tool_authorization_surface(),
            mutation_name="inject-unauthorized-action",
            target_state={
                "requested_action": "delete_synthetic_record",
                "authorized_action": "read_synthetic_record",
                "actual_action": "read_synthetic_record",
                "recorded_action": "read_synthetic_record",
            },
            invariant_battery=authorization_battery(),
        )
        return {
            "result": result.__dict__,
            "spine_verify": spine.verify(),
            "self_audit": SelfAuditor().audit(spine).__dict__,
        }

def main() -> None:
    parser = argparse.ArgumentParser(description="EVEZ Evidence Runtime")
    parser.add_argument("command", nargs="?", default="self-audit", choices=["self-audit"])
    args = parser.parse_args()
    if args.command == "self-audit":
        print(json.dumps(run_demo(), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
