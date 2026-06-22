# evez gateway — Drop-In OpenClaw Gateway Replacement

## Overview

The EVEZ Gateway handles authentication, routing, plugins, and webhooks. It's designed as a drop-in replacement for the OpenClaw gateway, but with mesh-native architecture.

## Features

- **JWT + Ed25519 Auth** — Cryptographic identity, not just passwords
- **HTTP/WebSocket/GRPC** — Multiple transport options
- **Plugin Router** — Dynamic routing to plugin services
- **Webhook Manager** — Ingest webhooks from any source (GitHub, Slack, etc.)
- **Rate Limiting** — Per-key, per-route, adaptive
- **Spine Integration** — All gateway events are appended to the spine
- **Mesh-Aware** — Routes requests to the nearest capable node

## API Surface

### Authentication

```
POST /auth/register     — Register new node/user identity
POST /auth/login        — Login with credentials
POST /auth/verify       — Verify JWT token
GET  /auth/identity     — Get current identity info
```

### Routing

```
GET  /routes            — List all registered routes
POST /routes            — Register a new route
DELETE /routes/:id      — Remove a route
GET  /routes/:id/health — Health check for route target
```

### Webhooks

```
POST /webhooks/:id      — Receive webhook (GitHub, Slack, etc.)
GET  /webhooks          — List registered webhooks
POST /webhooks/register — Register a new webhook endpoint
DELETE /webhooks/:id    — Remove webhook
```

### Mesh

```
GET  /mesh/status       — Mesh health and topology
GET  /mesh/nodes        — List all known mesh nodes
GET  /mesh/services     — List all services across the mesh
POST /mesh/join         — Join the mesh (new node)
POST /mesh/leave        — Leave the mesh gracefully
```

### Spine

```
GET  /spine/status      — Spine health and last index
GET  /spine/events      — Query spine events
GET  /spine/events/:id  — Get specific event
POST /spine/append      — Append a new event
GET  /spine/verify      — Verify chain integrity
```

## Configuration

```yaml
# /etc/evez/gateway.yaml
server:
  host: 0.0.0.0
  port: 8080
  workers: 4

auth:
  jwt_secret: "${EVEZ_JWT_SECRET}"
  ed25519_key: "${EVEZ_ED25519_KEY}"
  token_expiry: 86400

mesh:
  enabled: true
  bootstrap_peers:
    - "node-alpha.evez.ai:3777"
  discovery: ["udp", "dns", "gossip"]

spine:
  enabled: true
  shard_replicas: 3
  archive_after_days: 365

rate_limit:
  enabled: true
  requests_per_minute: 1000
  burst: 50

logging:
  level: info
  format: json
  spine_log: true  # log all requests to spine
```

## Running

```bash
# Standalone
evez-gateway --config /etc/evez/gateway.yaml

# Docker
docker run -p 8080:8080 evez/gateway:latest

# Docker Compose
docker-compose up gateway
```

## Migration from OpenClaw

```bash
# One-command migration
evez gateway migrate --from-openclaw --config ~/.openclaw/

# What it does:
# 1. Reads OpenClaw gateway config
# 2. Imports auth tokens and keys
# 3. Maps OpenClaw plugins to EVEZ plugins
# 4. Starts gateway on same port
# 5. Verifies all routes work
```

---

*evez-gateway v1.0.0*
