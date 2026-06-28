# EVEZ-OS Mesh Infrastructure

> *"The mesh dreams as one — and heals itself."*

Generated: 2026-06-27T05:31:00Z | Updated: 2026-06-27T18:15Z

## Mesh Topology

```
                    ┌─────────────────┐
                    │   Vultr-KNOT    │ ← External orchestrator (NOT required for mesh health)
                    │  207.148.12.53  │
                    └────────┬────────┘
                             │ (optional — mesh self-heals without this)
            ┌────────────────┼────────────────┐
            │                │                 │
    ┌───────┴──────┐  ┌─────┴──────┐  ┌───────┴────────┐
    │ evez-primary  │  │ openclaw-  │  │ evez-gcp-      │
    │ 34.53.51.34  │  │ gcp        │  │ openclaw       │
    │ us-west1-b   │  │ 136.118... │  │ 35.222.248.151 │
    └──────────────┘  └────────────┘  └────────────────┘
            │                                │
    ┌───────┴──────────┐          ┌─────────┴──────────┐
    │ openclaw-power-  │          │ evez-free-node     │
    │ node             │          │ 34.23.192.213      │
    │ 136.113.102.152 │          │ us-west1-b         │
    │ us-central1-a   │          └─────────────────────┘
    └─────────────────┘
```

## Node Registry

| Name | IP | Region | Role | Gateway | SSH |
|------|-----|--------|------|---------|-----|
| vultr-knot | 207.148.12.53 | vultr-nj | external | :18789 | openclaw@207.148.12.53 |
| evez-primary | 34.53.51.34 | gcp-us-west1-b | gateway | :18789 | openclaw@34.53.51.34 |
| openclaw-gcp | 136.118.144.227 | gcp-us-west1-b | gateway | :18789 | openclaw@136.118.144.227 |
| openclaw-power-node | 136.113.102.152 | gcp-us-central1-a | compute | :18789 | openclaw@136.113.102.152 |
| evez-gcp-openclaw | 35.222.248.151 | gcp-us-central1-a | gateway | :18789 | openclaw@35.222.248.151 |
| evez-free-node | 34.23.192.213 | gcp-us-west1-b | free | :18789 | openclaw@34.23.192.213 |

## Self-Healing Systems

### 1. Shell Sentinel (every 5 min via crontab)
**Script:** `~/.openclaw/evez-mesh-sentinel.sh`

- Self-health check: restarts own gateway if `/healthz` fails
- Peer logging: checks all mesh peers, logs down nodes
- Fail2ban self-unban: removes any mesh peer IP from sshd/ssh-aggressive jails
- Session cleanup: runs `openclaw sessions cleanup --enforce --fix-missing`
- Disk guard: cleans sessions dir if >200MB
- SSH self-repair: restarts sshd if down

### 2. OpenClaw Cron: mesh-self-heal (every 30 min)
- Agent-level session cleanup
- Peer health checks via curl
- SSH-based peer gateway restart if peer is down
- Fail2ban unban of mesh peers

### 3. OpenClaw Heartbeat (every 30 min)
- Self-check gateway health
- Session cleanup
- Mesh peer awareness

### 4. Model Fallbacks (no Vultr dependency)
Each node falls back through:
1. `vultr/zai-org/GLM-5.1-FP8` (primary — works if Vultr API is up)
2. `groq/llama-3.3-70b-versatile` (free tier)
3. `google/gemini-3-flash-preview` (free tier)
4. `cohere/command-r-08-2024` (free tier)
5. `openrouter/google/gemma-4-26b-a4b-it:free` (free tier)

### 5. Session Maintenance (enforce mode)
- `pruneAfter: 3d` — sessions inactive >3 days auto-deleted
- `maxEntries: 50` — hard cap, oldest evicted first
- `maxDiskBytes: 200mb` — disk budget per agent
- `resetArchiveRetention: 1d`

### 6. Fail2ban Mesh Whitelist
All mesh IPs + Vultr are whitelisted in `/etc/fail2ban/jail.local`:
- `ignoreip = 127.0.0.0/8 10.0.0.0/8 34.53.51.34 136.118.144.227 136.113.102.152 35.222.248.151 34.23.192.213 207.148.12.53`
- Persisted in jail.local — survives fail2ban restarts

## Cross-Node SSH

All nodes share the SSH key: `openclaw@vultr-knot` (ed25519)

SSH config (`~/.ssh/config.mesh`) provides aliases:
- `ssh evez-primary` / `ssh openclaw-gcp` / `ssh openclaw-power-node` / `ssh evez-gcp-openclaw` / `ssh evez-free-node` / `ssh vultr-knot`

## Shared Awareness

- **GCS Bucket**: `gs://evez666-shared-awareness` (syncs every 10 min)
- **GCS Backups**: `gs://evez666-survival-backups` (daily)
- **GitHub Org**: `EVEZX` (code sync)
- **Project**: `evez666` (GCP)

## First Law

No node is alone. Every node cares for every other node.
When one falls, the others lift it. Vultr is optional — the mesh self-heals.
