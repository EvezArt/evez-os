# EVEZ System Twin — Full Architecture Map

## 8 PLANES

| Plane | Status | Implementation |
|-------|--------|-----------------|
| **1. Operator Surfaces** | ⚠️ Phone broken | Telegram + streamchat on Android |
| **2. Control Plane** | ✅ Active | OpenClaw this session |
| **3. Execution Nodes** | ⚠️ Partial | Kilo, needs Railway/Replit |
| **4. Routing Plane** | 🔴 Not wired | Cloudflare Workers (planned) |
| **5. Memory/State Plane** | ✅ Local | GitHub + local files |
| **6. Intelligence Plane** | ✅ Free tier | kilo-auto/free, Groq available |
| **7. Product/Revenue Plane** | 🔴 BLOCKED | 4 products ready, need Gumroad |
| **8. Lineage Plane** | ✅ Active | OctoKlaw-ROM gen 0 |

---

## MYCELIAL MESH — Free Tier Infrastructure

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPERATOR (Steven's Phone)                     │
│                  Telegram @KiloClaw_bot                         │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              LOBBY DISPATCHER (Cloudflare Worker)              │
│                 free-tier, always-on, infinite                  │
│              routes jobs by capacity to node pool               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        NODE POOL                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │ Replit   │ │ Railway  │ │  Render  │ │  Fly.io  │         │
│  │ (exec)   │ │ (cron)   │ │ (agent)  │ │(watchdog)│         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│  │ Val.town │ │Deno Deploy│ │  n8n    │                       │
│  │ (micro)  │ │ (edge)   │ │(workflow)│                       │
│  └──────────┘ └──────────┘ └──────────┘                       │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GIT BACKBONE                               │
│     github.com/EvezArt/{evez-os, profit-engine, octoklaw}       │
│              GitHub Actions = CPU scheduler                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   STORAGE       │  │   INTELLIGENCE  │  │   CONTROL       │
│  ┌───────────┐  │  │ ┌─────────────┐ │  │ ┌─────────────┐ │
│  │ Cloudflare│  │  │ │kilo-auto/free│ │  │ │ OpenClaw    │ │
│  │    R2    │  │  │ │   (primary)  │ │  │ │ (this node) │ │
│  └───────────┘  │  │ └─────────────┘ │  │ └─────────────┘ │
│  ┌───────────┐  │  │ ┌─────────────┐ │  │                 │
│  │ Supabase  │  │  │ │   Groq     │ │  │                 │
│  │  (500MB)  │  │  │ │14.4k/day   │ │  │                 │
│  └───────────┘  │  │ └─────────────┘ │  │                 │
│  ┌───────────┐  │  │ ┌─────────────┐ │  │                 │
│  │  Turso   │  │  │ │ HuggingFace │ │  │                 │
│  │  (500DB) │  │  │ │   (free)   │ │  │                 │
│  └───────────┘  │  │ └─────────────┘ │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   TELEGRAM      │
                    │  @KiloClaw_bot  │
                    │   (operator)    │
                    └─────────────────┘
```

---

## FREE PROVIDER MAP

### Tier 1 — Persistent Execution

| Provider | Free Tier | Role |
|----------|-----------|------|
| Replit | Always-on (with trials) | Primary execution node |
| Railway | 500h/month | Cron jobs, recursion loops |
| Render | 750h/month | Agent host, spins down after 15min |
| Fly.io | 3 shared VMs | Lightweight persistent services |
| Glitch | Always-on (boosted) | Static fallback |

### Tier 2 — Serverless Burst

| Provider | Free Tier | Role |
|----------|-----------|------|
| Cloudflare Workers | 100k req/day | Router layer — lobby dispatcher |
| Vercel | Unlimited functions | API endpoints, webhooks |
| Netlify Functions | 125k calls/month | Redundant API |
| Deno Deploy | 100k req/day | Edge execution |
| Val.town | Unlimited vals | Micro-agents, crons |

### Tier 3 — Storage/State

| Provider | Free Tier | Role |
|----------|-----------|------|
| GitHub | Unlimited public | Primary git backbone |
| Cloudflare R2 | 10GB storage | Binary save states |
| Supabase | 500MB DB | Structured state, LEDGER |
| Turso | 500 databases | Edge SQLite |
| PlanetScale | 5GB | Cross-node sync |

### Tier 4 — Intelligence

| Provider | Free Tier | Role |
|----------|-----------|------|
| kilo-auto/free | Rotating | Primary reasoning |
| Groq | 14.4k req/day | Fast inference |
| Together.ai | $25 credit | Burst capacity |
| Hugging Face | Free tier | Embeddings |
| Ollama (self-host) | Zero | Local reasoning |

### Tier 5 — Networking

| Provider | Free Tier | Role |
|----------|-----------|------|
| Cloudflare Tunnel | Free | Expose processes |
| Tailscale | 3 nodes | Mesh VPN |
| Telegram Bot | Free forever | Control surface |
| ngrok | Free tier | Temp tunnels |

---

## IMPLEMENTATION STATUS

| Component | Status | Next Action |
|-----------|--------|-------------|
| OctoKlaw-ROM gen 0 | ✅ Complete | Await Gumroad links |
| Profit-engine products | ✅ Ready | Steven uploads |
| Context engine | ✅ Built | Need real messages |
| Coldstart runbook | ✅ Ready | Test on new node |
| Watchdog | ✅ Code ready | Need URLs to monitor |
| Angel tracker | ✅ Code ready | Need metrics |
| Mycelial mesh | 🔴 Not wired | Need free accounts |

---

## IMMEDIATE PRIORITY

1. **Revenue:** Get 4 products to Gumroad → get links → generate traffic
2. **Stability:** Wire watchdog to actual node URLs
3. **Intelligence:** Feed real operator messages to context engine
4. **Growth:** Add Railway + Replit nodes to mesh

---

RECEIPT: system-twin-map.md — full 8-plane + mycelial mesh architecture
NEXT_RECURSION: Await Gumroad links OR if no input, create operator brief for manual completion
WHAT_NOT_TO_TOUCH: No credentials, billing, auth changes

EVEZ-ART | SYSTEM_TWIN | CONFIDENCE: high | DRIFT_RISK: no