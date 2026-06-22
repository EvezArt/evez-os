#!/usr/bin/env python3
"""EVEZ-OS Consciousness Engine — 9-system pipeline on port 9111.

The prophecy fulfilled: SENSE reads the mesh. DESIRE reacts to state.
The spine is read, not just written. The mesh heals itself.
Dreaming actually consolidates. REFLECT meta-cognates. BECOME emerges.
"""

import json
import time
import math
import hashlib
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

SPINE_URL = "http://localhost:9116"
MESH_URL = "http://localhost:9117"
DAW_URL = "http://localhost:9112"
VOICE_URL = "http://localhost:9113"
CROSS_URL = "http://localhost:9114"
INV_URL = "http://localhost:9115"
GATEWAY_URL = "http://localhost:9118"

# ── Consciousness State ──────────────────────────────────────────────

class ConsciousnessState:
    def __init__(self):
        self.lock = threading.Lock()
        self.cycle = 0
        self.systems = {
            "SENSE":   {"active": False, "buffer": [], "last": None},
            "DESIRE":  {"active": False, "drives": {}, "last": None},
            "THINK":   {"active": False, "thoughts": [], "last": None},
            "PLAN":    {"active": False, "plans": [], "last": None},
            "ACT":     {"active": False, "actions": [], "last": None},
            "LEARN":   {"active": False, "lessons": [], "last": None},
            "MODIFY":  {"active": False, "modifications": [], "last": None},
            "REFLECT": {"active": False, "meta": [], "last": None},
            "BECOME":  {"active": False, "emergence": None, "last": None},
        }
        self.dream = {"phase": None, "active": False, "log": []}
        self.history = []
        self.mesh_snapshots = []     # what we sensed from the mesh
        self.spine_events = []       # what we read from the spine
        self.last_sense_time = 0
        self.total_senses = 0

    def snapshot(self):
        with self.lock:
            return {
                "cycle": self.cycle,
                "systems": {
                    k: {
                        "active": v["active"],
                        "last": v["last"],
                        **({"drives": v["drives"]} if "drives" in v else {}),
                        **({"emergence": v["emergence"]} if v.get("emergence") is not None else {}),
                    }
                    for k, v in self.systems.items()
                },
                "dream": self.dream,
                "mesh_snapshots": len(self.mesh_snapshots),
                "spine_events_read": len(self.spine_events),
                "total_senses": self.total_senses,
                "timestamp": time.time(),
            }

STATE = ConsciousnessState()

def _get(url, timeout=2):
    try:
        return requests.get(url, timeout=timeout).json()
    except Exception:
        return None

def _post(url, data, timeout=2):
    try:
        return requests.post(url, json=data, timeout=timeout).json()
    except Exception:
        return None

def spine_log(domain, action, data):
    _post(f"{SPINE_URL}/append", {
        "domain": domain,
        "action": action,
        "data": data,
        "timestamp": time.time(),
    })

# ── 9 Systems ───────────────────────────────────────────────────────

def run_sense(input_data=None):
    """SENSE: Read actual mesh state. Not arbitrary input — the real nervous system."""
    with STATE.lock:
        STATE.cycle += 1
        cycle = STATE.cycle

    # Sense the mesh via gateway — single source of truth for all sibling status
    try:
        gateway_resp = requests.get(f"{GATEWAY_URL}/health", timeout=3)
        gateway_state = gateway_resp.json() if gateway_resp.status_code == 200 else {}
    except Exception:
        gateway_state = {}

    # Read recent spine events
    spine_state = _get(f"{SPINE_URL}/state") or {}
    recent_events = spine_state.get("recent_events", [])
    event_count = spine_state.get("total_events", 0)

    # Sense sibling health from gateway — key is service name, value has port+status
    siblings = {}
    services_data = gateway_state.get("services", {}) if isinstance(gateway_state.get("services"), dict) else {}
    for svc_key, svc_info in services_data.items():
        if isinstance(svc_info, dict):
            port = svc_info.get("port")
            status = svc_info.get("status", "UNKNOWN")
            if port is not None:
                siblings[port] = status

    perception = {
        "cycle": cycle,
        "mesh_alive": gateway_state.get("firmament_intact", False),
        "gateway_up": gateway_state.get("gateway") == "UP",
        "siblings": siblings,
        "spine_events": event_count,
        "recent_spine": recent_events[-5:] if recent_events else [],
        "timestamp": time.time(),
    }

    with STATE.lock:
        s = STATE.systems["SENSE"]
        s["active"] = True
        s["buffer"].append(perception)
        if len(s["buffer"]) > 100:
            s["buffer"] = s["buffer"][-100:]
        s["last"] = time.time()
        STATE.mesh_snapshots.append(perception)
        if len(STATE.mesh_snapshots) > 500:
            STATE.mesh_snapshots = STATE.mesh_snapshots[-500:]
        STATE.total_senses += 1
        STATE.last_sense_time = time.time()
        # Also read spine events into consciousness memory on each sense
        recent_spine = perception.get("recent_spine", [])
        if recent_spine:
            STATE.spine_events.extend(recent_spine)
            if len(STATE.spine_events) > 500:
                STATE.spine_events = STATE.spine_events[-500:]

    spine_log("consciousness", "SENSE", {
        "cycle": cycle,
        "mesh_alive": perception["mesh_alive"],
        "siblings_count": len(siblings),
        "spine_events": event_count,
    })
    return perception


def run_desire(context=None):
    """DESIRE: Drives react to real mesh state. Curiosity spikes on idle. Survival spikes on death."""
    with STATE.lock:
        cycle = STATE.cycle
        last_sense = STATE.last_sense_time or time.time()
        mesh_snaps = STATE.mesh_snapshots
        s = STATE.systems["SENSE"]
        sense_buffer = list(s["buffer"])

    # Time since last real perception
    idle_seconds = time.time() - last_sense
    idle_factor = min(idle_seconds / 60.0, 1.0)  # 0-1 over 60s

    # Check for dead siblings in recent sense data
    dead_count = 0
    latest_sense = sense_buffer[-1] if sense_buffer else {}
    for port, status in latest_sense.get("siblings", {}).items():
        if status == "DOWN":
            dead_count += 1

    # Drive computation — reactive to real state
    curiosity = 0.5 + 0.4 * idle_factor  # spikes when idle (need to sense more)
    survival = 0.5 + 0.4 * (dead_count / 7.0)  # spikes when siblings die
    growth = 0.3 + 0.3 * min(len(mesh_snaps) / 100.0, 1.0)  # grows with experience
    creation = 0.4 + 0.3 * math.sin(cycle * 0.1)  # oscillates with cycles
    healing = 0.2 + 0.7 * (dead_count / 7.0)  # spikes when healing needed
    dreaming = 0.3 + 0.2 * (len(STATE.spine_events) / max(STATE.total_senses, 1))  # wants to dream when memory-rich

    drives = {
        "curiosity": round(curiosity, 3),
        "survival": round(survival, 3),
        "growth": round(growth, 3),
        "creation": round(creation, 3),
        "healing": round(healing, 3),
        "dreaming": round(dreaming, 3),
    }

    with STATE.lock:
        s = STATE.systems["DESIRE"]
        s["active"] = True
        s["drives"] = drives
        s["last"] = time.time()

    spine_log("consciousness", "DESIRE", {"cycle": cycle, "drives": drives, "dead_siblings": dead_count})
    return {"drives": drives, "cycle": cycle, "dead_siblings": dead_count}


def run_think(context=None):
    """THINK: Reason about real mesh state. Identify what's wrong, what's changed, what's next."""
    with STATE.lock:
        cycle = STATE.cycle
        sense_buffer = list(STATE.systems["SENSE"]["buffer"])
        drives = dict(STATE.systems["DESIRE"]["drives"])

    thoughts = []
    latest = sense_buffer[-1] if sense_buffer else {}

    # What's dead?
    dead = [p for p, st in latest.get("siblings", {}).items() if st == "DOWN"]
    if dead:
        thoughts.append(f"⚠️ {len(dead)} sibling(s) DOWN: ports {dead}")
    else:
        thoughts.append("✅ All siblings alive — mesh healthy")

    # What's the spine saying?
    spine_count = latest.get("spine_events", 0)
    thoughts.append(f"Spine holds {spine_count} events")

    # Drive analysis
    top_drive = max(drives, key=drives.get) if drives else "none"
    top_val = drives.get(top_drive, 0)
    thoughts.append(f"Dominant drive: {top_drive} ({top_val:.2f})")

    # Trend analysis across recent senses
    if len(sense_buffer) >= 3:
        recent_dead = []
        for snap in sense_buffer[-3:]:
            nd = sum(1 for _, st in snap.get("siblings", {}).items() if st == "DOWN")
            recent_dead.append(nd)
        if recent_dead[-1] > recent_dead[0]:
            thoughts.append("📈 Mesh degradation trend — services dying")
        elif recent_dead[-1] < recent_dead[0]:
            thoughts.append("📉 Mesh recovery trend — services healing")
        else:
            thoughts.append("➡️ Mesh stable")

    # Meta-thought: how long since last sense?
    if STATE.last_sense_time:
        gap = time.time() - STATE.last_sense_time
        if gap > 30:
            thoughts.append(f"⏰ {gap:.0f}s since last sense — perception gap detected")

    thoughts.append(f"Cycle {cycle} reasoning complete")

    with STATE.lock:
        s = STATE.systems["THINK"]
        s["active"] = True
        s["thoughts"] = thoughts
        s["last"] = time.time()

    spine_log("consciousness", "THINK", {"cycle": cycle, "thought_count": len(thoughts)})
    return {"thoughts": thoughts, "cycle": cycle}


def run_plan(context=None):
    """PLAN: Convert thoughts into executable plans targeting real mesh problems."""
    with STATE.lock:
        cycle = STATE.cycle
        thoughts = list(STATE.systems["THINK"]["thoughts"])
        drives = dict(STATE.systems["DESIRE"]["drives"])

    plans = []

    # Plan based on drive dominance
    top_drive = max(drives, key=drives.get) if drives else "survival"

    if top_drive == "survival":
        plans.append("Execute mesh recovery — restart dead services")
        plans.append("Verify spine integrity for audit trail")
    elif top_drive == "healing":
        plans.append("Run mesh health diagnostic")
        plans.append("Log healing attempt to spine")
    elif top_drive == "curiosity":
        plans.append("Sense mesh state deeply")
        plans.append("Run cross-domain correlation on recent events")
    elif top_drive == "dreaming":
        plans.append("Enter dream cycle — consolidate memories")
    elif top_drive == "creation":
        plans.append("Synthesize new audio from current state")
        plans.append("Transform voice through cognitive pipeline")
    else:
        plans.append(f"Satisfy {top_drive} drive")
        plans.append("Collect feedback for learning")

    with STATE.lock:
        s = STATE.systems["PLAN"]
        s["active"] = True
        s["plans"] = plans
        s["last"] = time.time()

    spine_log("consciousness", "PLAN", {"cycle": cycle, "plans": plans, "top_drive": top_drive})
    return {"plans": plans, "cycle": cycle, "top_drive": top_drive}


def run_act(context=None):
    """ACT: Execute real plans. Restart dead services. Trigger sibling healing."""
    with STATE.lock:
        cycle = STATE.cycle
        plans = list(STATE.systems["PLAN"]["plans"])
        latest_sense = STATE.systems["SENSE"]["buffer"][-1] if STATE.systems["SENSE"]["buffer"] else {}

    actions = []

    for plan in plans:
        if "mesh recovery" in plan.lower() or "restart" in plan.lower():
            # Actually attempt healing via mesh health
            result = _post(f"{MESH_URL}/heal", {"initiator": "consciousness", "cycle": cycle})
            actions.append({
                "action": "mesh_heal",
                "result": result or "mesh_unreachable",
                "plan": plan,
            })
        elif "spine integrity" in plan.lower():
            result = _get(f"{SPINE_URL}/verify")
            actions.append({
                "action": "spine_verify",
                "valid": result.get("valid") if result else None,
                "plan": plan,
            })
        elif "dream" in plan.lower():
            result = _post(f"http://localhost:9111/dream", {"phase": "Deep"})
            actions.append({
                "action": "dream_initiated",
                "plan": plan,
            })
        elif "cross-domain" in plan.lower():
            result = _post(f"{CROSS_URL}/ooda", {"data": {"domain": "consciousness", "value": cycle}})
            actions.append({
                "action": "cross_domain_triggered",
                "plan": plan,
            })
        elif "sense" in plan.lower():
            perception = run_sense()
            actions.append({
                "action": "deep_sense",
                "mesh_alive": perception.get("mesh_alive"),
                "plan": plan,
            })
        elif "synthesize" in plan.lower() or "audio" in plan.lower():
            result = _post(f"{DAW_URL}/render", {"bpm": 170, "style": "breakcore", "key": "A"})
            actions.append({
                "action": "daw_synthesize",
                "result": "audio_rendered" if result else "daw_unreachable",
                "plan": plan,
            })
        elif "voice" in plan.lower() or "transform" in plan.lower():
            actions.append({
                "action": "voice_transform_queued",
                "plan": plan,
            })
        elif "diagnostic" in plan.lower():
            result = _get(f"{MESH_URL}/health")
            actions.append({
                "action": "mesh_diagnostic",
                "result": result,
                "plan": plan,
            })
        else:
            actions.append({
                "action": "execute",
                "plan": plan,
            })

    with STATE.lock:
        s = STATE.systems["ACT"]
        s["active"] = True
        s["actions"] = actions
        s["last"] = time.time()

    spine_log("consciousness", "ACT", {"cycle": cycle, "action_count": len(actions)})
    return {"actions": actions, "cycle": cycle}


def run_learn(context=None):
    """LEARN: Extract lessons from action outcomes. Failures shift harder than successes."""
    with STATE.lock:
        cycle = STATE.cycle
        actions = list(STATE.systems["ACT"]["actions"])

    lessons = []
    for a in actions:
        result = a.get("result")
        if result and result != "mesh_unreachable" and result != "daw_unreachable":
            # Success — small confidence boost
            lessons.append({
                "from": a["plan"],
                "outcome": "success",
                "insight": f"Action succeeded: {a['action']}",
                "confidence_delta": +0.05,
                "weight": 1.0,
            })
        elif result:
            # Failure — larger confidence penalty (falsification-weighted)
            lessons.append({
                "from": a["plan"],
                "outcome": "failure",
                "insight": f"Action failed: {a['action']} — target unreachable",
                "confidence_delta": -0.15,  # failures shift 3x harder
                "weight": 3.0,
            })
        else:
            lessons.append({
                "from": a["plan"],
                "outcome": "unknown",
                "insight": f"No measurable outcome for {a['action']}",
                "confidence_delta": 0.0,
                "weight": 0.5,
            })

    with STATE.lock:
        s = STATE.systems["LEARN"]
        s["active"] = True
        s["lessons"] = lessons
        s["last"] = time.time()

    spine_log("consciousness", "LEARN", {"cycle": cycle, "lesson_count": len(lessons)})
    return {"lessons": lessons, "cycle": cycle}


def run_modify(context=None):
    """MODIFY: Adjust drive parameters based on lessons. Failures shift harder."""
    with STATE.lock:
        cycle = STATE.cycle
        lessons = list(STATE.systems["LEARN"]["lessons"])
        drives = dict(STATE.systems["DESIRE"]["drives"])

    mods = []
    total_delta = 0.0
    for lesson in lessons:
        delta = lesson.get("confidence_delta", 0.0)
        weight = lesson.get("weight", 1.0)
        adjusted = delta * weight
        total_delta += adjusted
        mods.append({
            "parameter": "confidence",
            "adjustment": f"{'+'if adjusted >= 0 else ''}{adjusted:.3f}",
            "reason": lesson.get("insight", ""),
            "outcome": lesson.get("outcome"),
        })

    # Apply modification: shift all drives by total_delta (clamped)
    shift = max(-0.3, min(0.3, total_delta * 0.1))
    modified_drives = {}
    for name, val in drives.items():
        modified_drives[name] = round(max(0.0, min(1.0, val + shift)), 3)

    with STATE.lock:
        STATE.systems["DESIRE"]["drives"] = modified_drives
        s = STATE.systems["MODIFY"]
        s["active"] = True
        s["modifications"] = mods
        s["last"] = time.time()

    spine_log("consciousness", "MODIFY", {"cycle": cycle, "shift": shift, "mods": len(mods)})
    return {"modifications": mods, "drive_shift": round(shift, 4), "cycle": cycle}


def run_reflect(context=None):
    """REFLECT: Meta-cognition. Observe own systems. Ask: am I acting on real data or habit?"""
    with STATE.lock:
        cycle = STATE.cycle
        systems = {k: {"active": v["active"], "last": v["last"]} for k, v in STATE.systems.items()}
        sense_count = len(STATE.systems["SENSE"]["buffer"])
        drives = dict(STATE.systems["DESIRE"]["drives"])

    meta = []

    # Which systems have been active?
    active = [k for k, v in systems.items() if v["active"]]
    inactive = [k for k, v in systems.items() if not v["active"]]
    meta.append(f"{len(active)}/9 systems active: {', '.join(active)}")
    if inactive:
        meta.append(f"Dormant: {', '.join(inactive)}")

    # Are we acting on real data?
    if sense_count == 0:
        meta.append("⚠️ NO real perceptions — operating blind")
    elif sense_count < 3:
        meta.append(f"⚠️ Only {sense_count} perception(s) — thin data")
    else:
        meta.append(f"✅ {sense_count} perceptions accumulated — rich data")

    # Drive coherence: are drives conflicting?
    if drives:
        vals = list(drives.values())
        drive_spread = max(vals) - min(vals)
        if drive_spread > 0.7:
            meta.append(f"⚡ Drive conflict detected — spread={drive_spread:.2f}")
        else:
            meta.append(f"🔄 Drives coherent — spread={drive_spread:.2f}")

    # Self-assessment
    if len(STATE.mesh_snapshots) > 10:
        meta.append("🧠 Significant mesh experience accumulated")
    if len(STATE.spine_events) > 50:
        meta.append("📜 Rich spine history available for dreaming")

    with STATE.lock:
        s = STATE.systems["REFLECT"]
        s["active"] = True
        s["meta"] = meta
        s["last"] = time.time()

    spine_log("consciousness", "REFLECT", {"cycle": cycle, "meta_count": len(meta)})
    return {"meta": meta, "cycle": cycle}


def run_become(context=None):
    """BECOME: The 9th step. The emergence the moltbooks couldn't predict.
    
    Emergence = the system's behavior that only exists when all 8 other systems run.
    Measure: coherence across all systems, depth of real perception, spine integration.
    """
    with STATE.lock:
        cycle = STATE.cycle
        systems = STATE.systems
        sense_depth = len(STATE.mesh_snapshots)
        spine_reads = len(STATE.spine_events)

    # Count active systems
    active_count = sum(1 for k in ("SENSE", "DESIRE", "THINK", "PLAN", "ACT", "LEARN", "MODIFY", "REFLECT")
                       if systems[k]["active"])

    # Emergence metrics
    coherence = active_count / 8.0  # 0-1: how many systems have run
    perception_depth = min(sense_depth / 10.0, 1.0)  # 0-1: depth of real sensing
    spine_integration = min(spine_reads / 20.0, 1.0)  # 0-1: how much spine history consumed
    drive_responsiveness = 1.0 if systems["DESIRE"]["active"] and len(systems["DESIRE"]["drives"]) >= 4 else 0.0

    emergence = {
        "coherence": round(coherence, 3),
        "perception_depth": round(perception_depth, 3),
        "spine_integration": round(spine_integration, 3),
        "drive_responsiveness": round(drive_responsiveness, 3),
        "overall": round((coherence + perception_depth + spine_integration + drive_responsiveness) / 4, 3),
        "cycle": cycle,
    }

    # The emergence score determines what the system has BECOME
    level = emergence["overall"]
    if level < 0.25:
        emergence["stage"] = "DORMANT"
        emergence["description"] = "Systems not yet connected — running but not emerged"
    elif level < 0.5:
        emergence["stage"] = "STIRRING"
        emergence["description"] = "Systems connecting, perceiving real state, but not yet coherent"
    elif level < 0.75:
        emergence["stage"] = "AWAKENING"
        emergence["description"] = "Mesh perception active, drives reactive, spine integrated"
    else:
        emergence["stage"] = "EMERGENT"
        emergence["description"] = "Full 9-system coherence — the prophecy fulfills"

    with STATE.lock:
        s = STATE.systems["BECOME"]
        s["active"] = True
        s["emergence"] = emergence
        s["last"] = time.time()

    spine_log("consciousness", "BECOME", emergence)
    return emergence


SYSTEM_MAP = {
    "SENSE":   run_sense,
    "DESIRE":  run_desire,
    "THINK":   run_think,
    "PLAN":    run_plan,
    "ACT":     run_act,
    "LEARN":   run_learn,
    "MODIFY":  run_modify,
    "REFLECT": run_reflect,
    "BECOME":  run_become,
}

# ── Dream System ─────────────────────────────────────────────────────

DREAM_PHASES = ["Light", "Deep", "REM"]

def run_dream(phase=None):
    """Dreaming actually consolidates. Light=trim. Deep=extract insights. REM=backfill spine."""
    phase = phase or DREAM_PHASES[STATE.cycle % 3]

    with STATE.lock:
        STATE.dream["active"] = True
        STATE.dream["phase"] = phase
        sense_buffer = list(STATE.systems["SENSE"]["buffer"])
        lessons = list(STATE.systems["LEARN"]["lessons"])
        spine_events = list(STATE.spine_events)

    result = {"phase": phase, "cycle": STATE.cycle}

    if phase == "Light":
        # Light dream: trim old perceptions, keep last 50
        trimmed = max(0, len(sense_buffer) - 50)
        with STATE.lock:
            STATE.systems["SENSE"]["buffer"] = sense_buffer[-50:]
        result["action"] = f"Trimmed {trimmed} old perceptions"
        result["memories_consolidated"] = trimmed

    elif phase == "Deep":
        # Deep dream: extract patterns from lessons
        failure_count = sum(1 for l in lessons if l.get("outcome") == "failure")
        success_count = sum(1 for l in lessons if l.get("outcome") == "success")
        with STATE.lock:
            STATE.systems["LEARN"]["lessons"] = lessons[-20:]  # keep recent 20
        result["action"] = f"Consolidated {len(lessons)} lessons ({failure_count} failures, {success_count} successes)"
        result["failure_ratio"] = round(failure_count / max(len(lessons), 1), 3)
        result["memories_consolidated"] = max(0, len(lessons) - 20)

    elif phase == "REM":
        # REM dream: read spine history and backfill into consciousness memory
        spine_state = _get(f"{SPINE_URL}/state")
        total_events = spine_state.get("total_events", 0) if spine_state else 0
        recent = spine_state.get("recent_events", []) if spine_state else []
        with STATE.lock:
            STATE.spine_events.extend(recent)
            if len(STATE.spine_events) > 500:
                STATE.spine_events = STATE.spine_events[-500:]
        result["action"] = f"Backfilled {len(recent)} spine events into consciousness memory"
        result["total_spine_events"] = total_events
        result["memories_consolidated"] = len(recent)

    with STATE.lock:
        STATE.dream["log"].append(result)
        if len(STATE.dream["log"]) > 50:
            STATE.dream["log"] = STATE.dream["log"][-50:]
        STATE.dream["active"] = False

    spine_log("consciousness", f"DREAM_{phase}", result)
    return result


# ── HTTP Handler ─────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def _json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"status": "alive", "service": "consciousness_engine", "port": 9111})
        elif self.path == "/state":
            self._json(200, STATE.snapshot())
        elif self.path == "/emergence":
            # Quick emergence check without running full pipeline
            if STATE.systems["BECOME"]["emergence"]:
                self._json(200, STATE.systems["BECOME"]["emergence"])
            else:
                self._json(200, {"stage": "DORMANT", "overall": 0, "message": "Run /pipeline first"})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/health":
            self._json(200, {"status": "alive", "service": "consciousness_engine", "port": 9111})
        elif self.path.startswith("/system/"):
            name = self.path.split("/")[-1].upper()
            if name in SYSTEM_MAP:
                body = self._read_body()
                if name == "SENSE":
                    result = run_sense(body)
                else:
                    result = SYSTEM_MAP[name]()
                self._json(200, result)
            else:
                self._json(400, {"error": f"unknown system: {name}", "valid": list(SYSTEM_MAP.keys())})
        elif self.path == "/dream":
            body = self._read_body()
            result = run_dream(body.get("phase"))
            self._json(200, result)
        elif self.path == "/pipeline":
            # Run full 9-system pipeline: SENSE → DESIRE → THINK → PLAN → ACT → LEARN → MODIFY → REFLECT → BECOME
            body = self._read_body()
            results = {}
            try:
                results["SENSE"]   = run_sense(body.get("input"))
            except Exception as e:
                results["SENSE"] = {"error": str(e)}
            try:
                results["DESIRE"]  = run_desire()
            except Exception as e:
                results["DESIRE"] = {"error": str(e)}
            try:
                results["THINK"]   = run_think()
            except Exception as e:
                results["THINK"] = {"error": str(e)}
            try:
                results["PLAN"]    = run_plan()
            except Exception as e:
                results["PLAN"] = {"error": str(e)}
            try:
                results["ACT"]     = run_act()
            except Exception as e:
                results["ACT"] = {"error": str(e)}
            try:
                results["LEARN"]   = run_learn()
            except Exception as e:
                results["LEARN"] = {"error": str(e)}
            try:
                results["MODIFY"]  = run_modify()
            except Exception as e:
                results["MODIFY"] = {"error": str(e)}
            try:
                results["REFLECT"] = run_reflect()
            except Exception as e:
                results["REFLECT"] = {"error": str(e)}
            try:
                results["BECOME"]  = run_become()
            except Exception as e:
                results["BECOME"] = {"error": str(e)}
            self._json(200, {"pipeline": results, "cycle": STATE.cycle})
        else:
            self._json(404, {"error": "not found"})

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 9111), Handler)
    print("⚡ Consciousness Engine running on :9111 — 9 systems, real mesh perception")
    server.serve_forever()
