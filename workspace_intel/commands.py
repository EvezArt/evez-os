#!/usr/bin/env python3
"""
Workspace Intel Commands - Generate actionable commands from audit data.
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

WORKSPACE = Path("/root/.openclaw/workspace")


def cmds_memory_cleanup() -> List[str]:
    """Commands to clean up memory"""
    memory = WORKSPACE / "memory"
    if not memory.exists():
        return []
    files = sorted(memory.glob("*.md"), key=lambda f: f.stat().st_mtime)
    to_archive = [f for f in files[:-5]]  # keep last 5
    return [f"mv {f.name} memory/archived/  # archive old note" for f in to_archive]


def cmds_heartbeat_check() -> List[str]:
    """Commands to check heartbeat state"""
    hb = WORKSPACE / "HEARTBEAT.md"
    lines = 0
    if hb.exists():
        lines = len(hb.read_text().splitlines())
    return [
        f"# HEARTBEAT.md has {lines} lines",
        f"# Recommended: keep it under 30 lines for fast reads",
    ]


def cmds_skills_install() -> List[str]:
    """Recommended skills to install"""
    existing = set((WORKSPACE / "skills").glob("*/SKILL.md")) if (WORKSPACE / "skills").exists() else set()
    recommended = [
        ("github", "GitHub operations"),
        ("healthcheck", "Host security hardening"),
        ("weather", "Weather forecasts"),
    ]
    return [
        f"openclaw plugins install skill-{name}  # {desc}"
        for name, desc in recommended
    ]


def cmds_factory_housekeeping() -> List[str]:
    """Factory maintenance commands"""
    return [
        "# Archive old factory logs",
        f"# Last cycle: checkpoint.json shows cycle 39 (2026-04-18)",
        "# Factory has 0 deployments despite 100 discoveries",
        "openclaw doctor  # run health check",
    ]


def all_commands() -> List[str]:
    """All actionable commands grouped"""
    return {
        "memory": cmds_memory_cleanup(),
        "heartbeat": cmds_heartbeat_check(),
        "skills": cmds_skills_install(),
        "factory_housekeeping": cmds_factory_housekeeping(),
    }


if __name__ == "__main__":
    print(json.dumps(all_commands(), indent=2))