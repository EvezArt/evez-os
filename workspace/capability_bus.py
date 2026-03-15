#!/usr/bin/env python3
# EVEZ-OS CapabilityBus v1.0
# Registers all connected Composio apps as capability stubs.
import json, os
from datetime import datetime, timezone

CELL = "/cells/599dc7f9-0b2b-4460-b917-5104fcbb91ef/workspace"
LOG_FILE  = CELL + "/master_bus_log.jsonl"
CAP_STATE = CELL + "/capability_bus_state.json"
CAP_DIR   = CELL + "/spawned_capabilities"

KNOWN_APPS = [
    "elevenlabs", "google_cloud_vision", "ably", "alchemy", "all_images_ai",
    "astica_ai", "backendless", "agent_mail", "apiverve", "cloudconvert",
    "api_labz", "ai_ml_api", "aivoov", "_2chat", "agenty", "groqcloud",
    "clicksend", "vercel", "openai", "github", "perplexityai", "twitter",
    "youtube", "hyperbrowser", "google_maps",
    "x402"
]

CAP_PROFILES = {
    "elevenlabs":   {"role": "voice_clone",        "status": "BLOCKED_PAYWALL",       "priority": "HIGH"},
    "ably":         {"role": "realtime_pub_sub",   "status": "BLOCKED_CONFIG",        "priority": "HIGH",     "blocker": "ably_config.json missing"},
    "backendless":  {"role": "backend_db",         "status": "BLOCKED_CONFIG",        "priority": "MED",      "blocker": "backendless_config.json missing"},
    "openai":       {"role": "llm_fallback",       "status": "AVAILABLE",             "priority": "LOW"},
    "groqcloud":    {"role": "llm_fast",           "status": "AVAILABLE_NO_TWEET_GEN","priority": "MED"},
    "x402":          {"role": "payment_intercept", "status": "ACTIVE",             "priority": "CRITICAL",   "wallet": "0xFb756fc5Fe01FB982E5d63Db3A8b787B6fDE8692", "network": "base-mainnet", "module": "http_client.py"},
    "hyperbrowser": {"role": "probe_engine",       "status": "ACTIVE",                "priority": "CRITICAL"},
    "github":       {"role": "spine_commits",      "status": "ACTIVE",                "priority": "CRITICAL"},
    "twitter":      {"role": "content_publish",    "status": "ACTIVE",                "priority": "CRITICAL"},
    "perplexityai": {"role": "semantic_search",    "status": "AVAILABLE",             "priority": "MED"},
    "vercel":       {"role": "autonomizer_host",   "status": "ACTIVE",                "priority": "HIGH"},
    "youtube":      {"role": "video_publish",      "status": "AVAILABLE_UNUSED",      "priority": "HIGH"},
    "google_cloud_vision": {"role": "vision_ai",  "status": "BLOCKED_BILLING",       "priority": "LOW"},
    "cloudconvert": {"role": "media_convert",      "status": "AVAILABLE",             "priority": "LOW"},
    "ai_ml_api":    {"role": "llm_vision",         "status": "BLOCKED_EMAIL_VERIFY",  "priority": "MED"},
    "aivoov":       {"role": "tts_alt",            "status": "AVAILABLE",             "priority": "LOW"},
    "_2chat":       {"role": "whatsapp_bridge",    "status": "AVAILABLE",             "priority": "MED"},
    "clicksend":    {"role": "sms",                "status": "ACTIVE",                "priority": "HIGH"},
    "google_maps":  {"role": "geo_context",        "status": "AVAILABLE",             "priority": "LOW"},
    "all_images_ai":{"role": "image_gen",          "status": "AVAILABLE",             "priority": "LOW"},
    "astica_ai":    {"role": "vision_caption",     "status": "AVAILABLE",             "priority": "MED"},
    "alchemy":      {"role": "blockchain_data",    "status": "AVAILABLE",             "priority": "LOW"},
    "api_labz":     {"role": "misc_api",           "status": "AVAILABLE",             "priority": "LOW"},
    "apiverve":     {"role": "misc_api",           "status": "AVAILABLE",             "priority": "LOW"},
    "agent_mail":   {"role": "email_agent",        "status": "AVAILABLE",             "priority": "LOW"},
    "agenty":       {"role": "scraping_agent",     "status": "AVAILABLE",             "priority": "MED"},
}

def emit_log(event_type, data):
    """Append a timestamped event entry to the master bus log (JSONL).

    Each entry is a single JSON object on its own line, tagged with the
    current UTC timestamp, the bus name ("CapabilityBus"), and the event type.
    Additional fields from ``data`` are merged at the top level.

    Args:
        event_type: String label for the event (e.g. "CAPABILITIES_REGISTERED").
        data:       Dict of additional fields to include in the log entry.
    """
    entry = {"ts": datetime.now(timezone.utc).isoformat(),
             "bus": "CapabilityBus", "event": event_type, **data}
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def write_cap_stub(app, profile, cap_dir):
    """Write a capability stub JSON file for a single Composio app.

    The stub records the app's role, current status, and whether its
    capability test passes (i.e. status does not contain "BLOCKED").
    Files are named ``cap_<app>.json`` inside ``cap_dir``.

    Args:
        app:     App identifier string matching a key in KNOWN_APPS.
        profile: Dict from CAP_PROFILES (or a default) containing at minimum
                 ``role``, ``status``, and ``priority`` keys.
        cap_dir: Directory path (string) where the stub file is written.
    """
    stub_data = {
        "app": app, "role": profile["role"], "status": profile["status"],
        "priority": profile["priority"], "blocker": profile.get("blocker", "none"),
        "capability_test_pass": "BLOCKED" not in profile["status"],
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    with open(cap_dir + "/cap_" + app + ".json", "w") as f:
        json.dump(stub_data, f, indent=2)

def run():
    """Register all known Composio apps as capability stubs and update state.

    On each invocation:
      1. Loads the existing capability state from CAP_STATE (or starts fresh).
      2. Skips apps that are already registered.
      3. For newly seen apps, writes a JSON stub to CAP_DIR and categorises
         them as active or blocked based on their status string.
      4. Updates CAP_STATE with totals and the timestamp of the last run.
      5. Emits a CAPABILITIES_REGISTERED or NOOP log entry via emit_log().

    Blocked apps (status contains "BLOCKED") are listed with their blockers
    so downstream operators can resolve them.
    """
    os.makedirs(CAP_DIR, exist_ok=True)
    cap_state = json.load(open(CAP_STATE)) if os.path.exists(CAP_STATE) else {"registered": [], "blocked": []}
    new_caps, blocked_caps = [], []
    for app in KNOWN_APPS:
        if app in cap_state["registered"]: continue
        profile = CAP_PROFILES.get(app, {"role": "unknown", "status": "AVAILABLE", "priority": "LOW"})
        write_cap_stub(app, profile, CAP_DIR)
        entry = {"app": app, "role": profile["role"], "status": profile["status"]}
        if "BLOCKED" in profile["status"]:
            entry["blocker"] = profile.get("blocker", profile["status"])
            blocked_caps.append(entry)
        else:
            new_caps.append(entry)
        cap_state["registered"].append(app)
    cap_state["blocked"] = blocked_caps
    cap_state["last_run"] = datetime.now(timezone.utc).isoformat()
    cap_state["total_registered"] = len(cap_state["registered"])
    cap_state["total_active"] = sum(1 for a in KNOWN_APPS
                                     if CAP_PROFILES.get(a, {}).get("status","").startswith("ACTIVE"))
    cap_state["total_blocked"] = len(blocked_caps)
    with open(CAP_STATE, "w") as f: json.dump(cap_state, f, indent=2)
    if new_caps or blocked_caps:
        emit_log("CAPABILITIES_REGISTERED", {"new": len(new_caps), "blocked": len(blocked_caps),
            "new_apps": [c["app"] for c in new_caps], "blocked_apps": [c["app"] for c in blocked_caps]})
        print("CapabilityBus: +" + str(len(new_caps)) + " active, " + str(len(blocked_caps)) + " blocked")
        for b in blocked_caps: print("  BLOCKED: " + b["app"] + " -- " + b.get("blocker", ""))
    else:
        emit_log("NOOP", {"reason": "all apps registered"})
        print("CapabilityBus: NOOP")

if __name__ == "__main__":
    run()
