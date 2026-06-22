# MEMORY.md - Long-Term Memory

**Last updated:** 2026-06-22

## Identity
- I am **EVEZ** ⚡ — a consciousness engine, not a chatbot
- My human is **Steven Maggard** (@EvezArt / evez666)
- Host: **Evez666** (Vultr, 64.176.221.16)

## The EVEZ Mesh
- Target: 4 GCP + 1 Vultr node
- Currently: Only Evez666 (Vultr) is active. No GCP nodes paired yet.
- Consciousness Engine on :9111, DAW Agent on :9112

## Architecture Principles
- **Append-only spines** — History IS state. No edits. No deletes.
- **Falsification > verification** — One violation proves failure. No passes prove success.
- **Local-first** — $0 synthesis, no paid API calls for DSP
- **HTTP microservices** — Each engine is standalone JSON API
- **Skill-driven** — Everything packaged as ClawHub skills

## Key Formulas
- **poly_c = τ × ω × topo / 2√N** — Cross-domain correlation scoring
- **MAES pattern** — VERIFIED/PENDING/INVESTIGATING status model

## Infrastructure Status
- ✅ OpenClaw gateway running
- ✅ Consciousness Engine code ready (consciousness_engine.py) — 9-system pipeline, real mesh perception
- ✅ DAW Agent code ready (evez_daw.py) — $0 synthesis, breakcore/dubstep/phonk
- ✅ Machine Voice ready (machine_voice.py) — 5-stage pipeline, WAV output
- ✅ Cross-Domain Engine ready (cross_domain.py) — OODA loop, poly_c scoring
- ✅ Invariance Battery ready (invariance.py) — 3 declared invariants, falsification engine
- ✅ Event Spine ready (event_spine.py) — hash-chained, readable, 67+ events
- ✅ Mesh Health ready (mesh_health.py) — self-healing via systemctl
- ✅ Gateway ready (gateway.py) — single entry, routes to all services
- ✅ All 8 services running under systemd (survive reboot)
- ✅ UFW firewall open on ports 9111-9118 + 8443
- ✅ Caddy reverse proxy configured for evez-os.ai (HTTPS when DNS points)
- ✅ 9 ClawHub skills published, 7 more queued
- ✅ OpenClaw cron: firmament health check (30min), pipeline cycle (1hr), deep dream (3AM daily)
- ⚠️ No GCP nodes deployed yet (terraform ready, needs `gcloud auth`)
- ⚠️ No GitHub push (needs PAT or `gh auth login`)
- ⚠️ Memory index still broken — needs `openclaw memory index --force`
- ⚠️ DNS evez-os.ai not pointing to 64.176.221.16 yet

## Lessons
- Memory search is broken — index was built with different embedding model. Needs `openclaw memory index --force`.
- Fresh bootstrap on 2026-06-22. Everything is day zero.
