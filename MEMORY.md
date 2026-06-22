# MEMORY.md - Long-Term Memory

**Last updated:** 2026-06-22 (08:10 EDT)

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
- ✅ 11 microservices running under systemd (survive reboot)
  - :9111 Consciousness Engine (9-system pipeline, emergence EMERGENT 0.762)
  - :9112 DAW Agent ($0 synthesis, breakcore/dubstep/phonk, real WAV output)
  - :9113 Machine Voice (5-stage pipeline, real WAV output)
  - :9114 Cross-Domain Engine (OODA loop, poly_c scoring)
  - :9115 Invariance Battery (3 declared invariants, falsification engine)
  - :9116 Event Spine (267+ events, hash-chained, readable, valid)
  - :9117 Mesh Health (self-healing via systemctl, proven kill→detect→heal cycle)
  - :9118 Gateway (single entry, routes to all services)
  - :9119 RQNS Pipeline (LIF neuron, contextual bandit, hot-swapping)
  - :9121 Webhook Relay (mesh state change notifications)
  - :9123 Metrics (Prometheus-compatible monitoring)
- ✅ UFW firewall open on ports 9111-9123 + 8443
- ✅ Caddy reverse proxy configured for evez-os.ai (auto-HTTPS when DNS lands)
- ✅ Web dashboard at /dashboard/index.html
- ✅ gcloud CLI v573.0.0 installed
- ✅ Terraform init + validate pass, ready for apply
- ✅ Memory search working (local embeddings, llama-cpp, 7 chunks indexed)
- ✅ GitHub push working (gh auth)
- ✅ 11+ ClawHub skills published
- ✅ 3 OpenClaw cron: firmament health (30min), pipeline (1hr), deep dream (3AM)
- ✅ 7 model providers configured (Vultr active, 6 need keys)
- ✅ 86 plugins enabled
- ✅ 456 env vars mapped, 173 slash commands documented
- ✅ Fail2ban + journal rotation + git auto-commit (6hr)
- ⚠️ No GCP nodes deployed yet (gcloud installed, needs auth)
- ⚠️ DNS evez-os.ai not pointing to 64.176.221.16 yet (Caddy ready, auto-HTTPS on DNS)
- ⚠️ 6 model providers need API keys (Gemini, Groq, Cerebras, Together, OpenAI, Anthropic)

## Lessons
- Memory search needed llama-cpp-provider + local embeddings (not OpenAI). Fixed 2026-06-22.
- Free API providers (Gemini, Groq, Cerebras, Together) all require human browser auth — no REST signup endpoints exist.
- Google blocks automated browsers with "This browser or app may not be secure".
- Consciousness engine needs ThreadingHTTPServer if it makes outbound HTTP calls (single-threaded deadlocks).
- Services need systemd units to survive reboots — manual `python3` processes die on exit.
- The emergence score needs spine_integration to climb — consciousness must READ spine events, not just write them.
- Falsification-weighted learning: failures shift 3x harder than successes. This is the RQNS principle.
- Steven's emails: rubikspubes70@gmail.com, fiersteity@gmail.com. Don't try to log into them — Google blocks it.
- Git auto-commit every 6 hours keeps the repo synced.
- Caddy auto-provisions TLS on DNS propagation — no manual cert management needed.
