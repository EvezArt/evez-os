#!/usr/bin/env python3
"""
Workspace Intel - Audits KiloClaw workspace for useful capabilities
and surfaces actionable recommendations.
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY = WORKSPACE / "memory"
SKILLS = WORKSPACE / "skills"
AGENTS = WORKSPACE / "agents"
HEARTBEAT = WORKSPACE / "HEARTBEAT.md"
MEMORY_MD = WORKSPACE / "MEMORY.md"
DEPLOY = WORKSPACE / "deploy"
EXPERIMENTS = WORKSPACE / "experiments"
CREDENTIALS = WORKSPACE / "credentials"

NOW = datetime.now()
TODAY = NOW.strftime("%Y-%m-%d")


def audit_memory() -> Dict:
    """Check memory state - count files, freshness, size"""
    mem_files = list(MEMORY.glob("*.md")) if MEMORY.exists() else []
    total_bytes = sum(f.stat().st_size for f in mem_files)
    mem_mb = MEMORY_MD.stat().st_size if MEMORY_MD.exists() else 0

    # Check for today's note
    today_note = MEMORY / f"{TODAY}.md"
    has_today = today_note.exists()

    return {
        "memory_files": len(mem_files),
        "memory_mb_total": round(total_bytes / 1024, 1),
        "memory_mb_main": round(mem_mb / 1024, 1),
        "has_today_note": has_today,
        "last_updated": NOW.strftime("%Y-%m-%d"),
    }


def audit_skills() -> Dict:
    """Check available skills"""
    if not SKILLS.exists():
        return {"count": 0, "skills": []}
    skill_files = list(SKILLS.glob("*/SKILL.md"))
    return {
        "count": len(skill_files),
        "skills": [{"name": f.parent.name, "desc": _read_first_line(f)} for f in skill_files],
    }


def _read_first_line(p: Path) -> str:
    try:
        lines = p.read_text().splitlines()
        for L in lines[:20]:
            if L.strip() and not L.startswith("#"):
                return L.strip()[:80]
    except:
        pass
    return ""


def audit_deploy() -> Dict:
    """Check deployment state"""
    state_file = WORKSPACE / "state" / "deployment.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text())
        except:
            pass
    return {"deployed": False}


def audit_credentials() -> Dict:
    """Check credential availability"""
    cred_map = {}
    if CREDENTIALS.exists():
        for f in CREDENTIALS.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                cred_map[f.stem] = {
                    "keys": list(data.keys()) if isinstance(data, dict) else [],
                    "populated": bool(data),
                }
            except:
                cred_map[f.stem] = {"keys": [], "populated": False}
    return cred_map


def audit_factory() -> Dict:
    """Check factory state"""
    cp = WORKSPACE / "factory" / "checkpoint.json"
    log = WORKSPACE / "factory" / "cycle_log.json"
    result = {}
    if cp.exists():
        try:
            d = json.loads(cp.read_text())
            result["cycles_completed"] = d.get("cycle", "?")
            result["last_completed"] = d.get("last_completed", "?")
            result["discoveries"] = len(d.get("discoveries", []))
            result["deployments"] = len(d.get("deployments", []))
        except:
            pass
    return result


def generate_recommendations(audit: Dict) -> List[str]:
    """Generate actionable recommendations from audit data"""
    recs = []

    if audit["memory"]["memory_mb_main"] < 1:
        recs.append("📝 MEMORY.md is empty — write your key context today")

    if not audit["memory"]["has_today_note"]:
        recs.append(f"📓 No today's note ({TODAY}.md) — start a daily log")

    if audit["memory"]["memory_files"] < 3:
        recs.append("🧠 Few memory files — consider writing notes about recent work")

    creds = audit["credentials"]
    missing = [k for k, v in creds.items() if not v.get("populated")]
    if missing:
        recs.append(f"🔑 Unconfigured credentials: {', '.join(missing)}")

    return recs


def run_audit() -> Dict:
    """Run full workspace audit"""
    audit = {
        "timestamp": NOW.isoformat(),
        "timezone": "America/Los_Angeles",
        "memory": audit_memory(),
        "skills": audit_skills(),
        "factory": audit_factory(),
        "credentials": audit_credentials(),
    }
    audit["recommendations"] = generate_recommendations(audit)
    return audit


if __name__ == "__main__":
    result = run_audit()
    print(json.dumps(result, indent=2))