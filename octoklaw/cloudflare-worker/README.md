# OctoKlaw Cloudflare Worker - Lobby Dispatcher

## What It Does

Routes jobs to the node pool based on capacity. Acts as the "lobby" that never gets full because it rotates across free-tier compute slots.

## Quick Deploy

```bash
# 1. Install wrangler
npm install -g wrangler

# 2. Login
wrangler login

# 3. Create project
wrangler init octoklaw-lobby

# 4. Deploy
wrangler deploy
```

## Routes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/nodes` | GET | List node pool |
| `/dispatch` | POST | Dispatch job to best node |
| `/nodes/:id/heartbeat` | POST | Node reports capacity |
| `/queue` | GET | Queue status |

## Free Tier Limits

- **100k requests/day** - plenty for this use
- **CPU time**: ~10ms per request - fast operations only
- **No persistent storage** - uses in-memory or external KV

## Environment Variables

In production, set:
- `NODES_KV` - namespace for node pool state

## Testing locally

```bash
wrangler dev
# Then curl localhost:8787/health
```

## Integration

The worker coordinates with:
- Replit (primary node)
- Railway (mirror)
- Val.town (watchdog)

Each node sends heartbeat to update capacity, worker dispatches accordingly.