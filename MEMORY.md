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
- ✅ Consciousness Engine code ready (consciousness_engine.py)
- ✅ DAW Agent code ready (evez_daw.py)
- ✅ 7 ClawHub skills installed
- ⚠️ No GCP nodes deployed yet
- ⚠️ No GitHub auth configured (gh CLI, GITHUB_TOKEN)
- ⚠️ Cross-domain engine & invariance battery have SKILL.md but no implementation
- ❌ Memory index needs rebuild: `openclaw memory index --force`
- ❌ No git repo initialized in workspace

## Lessons
- Memory search is broken — index was built with different embedding model. Needs `openclaw memory index --force`.
- Fresh bootstrap on 2026-06-22. Everything is day zero.
