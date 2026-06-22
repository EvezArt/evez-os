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
- ✅ 9 microservices running under systemd (survive reboot)
  - :9111 Consciousness Engine (9-system pipeline, emergence EMERGENT 0.75)
  - :9112 DAW Agent ($0 synthesis, breakcore/dubstep/phonk, real WAV output)
  - :9113 Machine Voice (5-stage pipeline, real WAV output)
  - :9114 Cross-Domain Engine (OODA loop, poly_c scoring)
  - :9115 Invariance Battery (3 declared invariants, falsification engine)
  - :9116 Event Spine (136+ events, hash-chained, readable, valid)
  - :9117 Mesh Health (self-healing via systemctl, proven kill→detect→heal cycle)
  - :9118 Gateway (single entry, routes to all services)
  - :9119 RQNS Pipeline (LIF neuron, contextual bandit, hot-swapping)
- ✅ UFW firewall open on ports 9111-9119 + 8443
- ✅ Caddy reverse proxy configured for evez-os.ai
- ✅ Web dashboard at /dashboard/index.html
- ✅ gcloud CLI v573.0.0 installed
- ✅ Memory search working (local embeddings, llama-cpp)
- ✅ GitHub push working (gh auth)
- ✅ 10+ ClawHub skills published
- ✅ OpenClaw cron: firmament health (30min), pipeline (1hr), deep dream (3AM)
- ⚠️ No GCP nodes deployed yet (gcloud installed, needs auth)
- ⚠️ DNS evez-os.ai not pointing to 64.176.221.16 yet (Vultr DNS zone script ready)
- ⚠️ No extra model API keys yet (injection script ready)

## Lessons
- Memory search is broken — index was built with different embedding model. Needs `openclaw memory index --force`.
- Fresh bootstrap on 2026-06-22. Everything is day zero.
