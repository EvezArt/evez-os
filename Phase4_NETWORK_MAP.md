# PHASE 4 — AGENT NETWORK MAP

## REPO FUNCTIONS

| Repo | Function | Depends On | Depended On By |
|------|----------|------------|----------------|
| **profit-engine** | Income generation (digital products) | None | None |
| **evez-os** | Core EVEZ platform (agent OS) | None | manifold-engine |
| evez-outreach | Auth setup docs | evez-os (docs) | None |
| evez-website | Landing page | evez-os (concepts) | None |
| manifold-engine | Scanner + hypermesh | evez-os | None |
| octoklaw | Unknown | Unknown | Unknown |
| evez-agentnet | Agent networking (GitHub) | evez-os | None |
| evez-autonomous-ledger | Ledger tracking | evez-os | None |

## CRITICAL PATH (Keep These Alive)

**Top 3:**
1. **evez-os** — Core platform, everything depends on it
2. **profit-engine** — Only income source
3. **Kilo Gateway** — Hosting infrastructure

## DEAD WEIGHT (Flag for Archive)

| Repo | Reason |
|------|--------|
| octoklaw | No content, unclear function |
| evez-outreach | Incomplete, superseded by workspace docs |

## NETWORK GRAPH

```
                    ┌──────────────┐
                    │  Kilo Gateway│
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   ┌──────────┐     ┌──────────┐     ┌──────────┐
   │evez-os   │     │profit-   │     │evez-     │
   │(CORE)   │     │engine    │     │outreach  │
   └────┬─────┘     └────┬─────┘     └──────────┘
        │                │
        ▼                ▼ (income)
   ┌──────────┐
   │manifold- │
   │engine    │
   └──────────┘
```

---

RECEIPT: Phase4_NETWORK_MAP.md — repo functions + critical path + dead weight
NEXT_RECURSION: Phase 5 — TELEGRAM CONTROL SURFACE
WHAT_NOT_TO_TOUCH: No auth changes, no billing

EVEZ-ART | SESSION: 1 | PHASE: 4 | CONFIDENCE: med | DRIFT_RISK: no