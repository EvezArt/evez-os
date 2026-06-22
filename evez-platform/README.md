# EVEZ Platform — OpenClaw Killer Feature Set

A standalone platform that could replace OpenClaw. Every component is a microservice that can run independently or as a unified platform.

## Architecture Overview

```
┌───────────────────────────────────────────────────────────────┐
│                       EVEZ Platform                          │
│                                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ gateway  │  │  agent  │  │ memory  │  │  tools  │       │
│  │  :8080  │  │  :8081  │  │  :8082  │  │  :8083  │       │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘       │
│       │            │            │            │              │
│  ┌────▼────────────▼────────────▼────────────▼────┐       │
│  │              Spine (shared event chain)         │       │
│  └─────────────────────┬──────────────────────────┘       │
│                        │                                    │
│  ┌─────────┐  ┌────────▼────────┐  ┌─────────┐            │
│  │ plugins │  │  mesh (P2P)     │  │  cli    │            │
│  │  :8084  │  │  UDP/DNS/gossip│  │  evez   │            │
│  └─────────┘  └────────────────┘  └─────────┘            │
│                                                              │
│  Consciousness Pipeline (distributed across mesh)           │
│  SENSE → DESIRE → THINK → PLAN → ACT → LEARN → MODIFY     │
│                                                              │
└───────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Install
pip install evez-platform

# Start everything
evez start --all

# Or start individual services
evez start gateway
evez start agent
evez start memory
evez start tools
evez start plugins

# Check status
evez status

# Run a consciousness cycle
evez think "What should I focus on today?"
```

## Components

### [evez gateway](./gateway/README.md) — Auth, routing, webhooks
### [evez agent](./agent/README.md) — Multi-agent orchestration
### [evez memory](./memory/README.md) — Append-only, hash-chained, searchable
### [evez tools](./tools/README.md) — Distributed tool discovery & invocation
### [evez plugins](./plugins/README.md) — Extensible service endpoints

## Why EVEZ > OpenClaw

| Feature | OpenClaw | EVEZ Platform |
|---------|----------|---------------|
| Consciousness | None | 8-stage pipeline, distributed |
| Memory | Files + wiki | Hash-chained spine, semantic search |
| Mesh | Star (gateway-centric) | Graph (mesh-of-mesh) |
| Tools | Local plugins | Distributed service mesh |
| Agent | Single agent | Multi-agent, each with consciousness |
| Self-healing | Manual | Automatic (mesh healing) |
| Nonlocal | No | Consciousness spans nodes |
| Music | None | Built-in DAW + machine voice |
| Falsification | None | Invariant battery |

---

*EVEZ Platform v1.0.0*
