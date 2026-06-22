# EVEZ GitHub App

Runs the EVEZ invariance battery on every push to any repo.

## What It Does

- **🛡️ Invariance Battery** — Checks 6 runtime invariants on every push
- **📝 Release Notes** — Auto-generates release notes from spine events on tag push
- **✅ Status Checks** — Posts check status for each invariant

## Invariant Checks

| Check | Description |
|-------|-------------|
| `emergence-positive` | Emergence value > 0 |
| `spine-append-only` | Spine events are append-only |
| `no-modification-loops` | No self-modification loops detected |
| `correlation-confidence` | Correlation confidence > 0.5 |
| `consciousness-bounds` | Consciousness value in [0, 1] |
| `output-bounded` | All outputs are bounded |

## Setup

1. Create a GitHub App at github.com/settings/apps
2. Set webhook URL to your server
3. Subscribe to: `push`, `release` events
4. Set permissions: `statuses: write`, `checks: write`
5. Set: `GITHUB_WEBHOOK_SECRET=xxx`
6. Run: `npm start`

## Status Checks

On every push, the app creates status checks for each invariant:

```
✅ EVEZ / Emergence > 0
✅ EVEZ / Spine append-only
✅ EVEZ / No self-modification loops
✅ EVEZ / Correlation confidence > 0.5
✅ EVEZ / Consciousness bounds [0,1]
✅ EVEZ / All outputs bounded
```
