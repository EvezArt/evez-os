# EVEZ SELF-PROPAGATING DAEMON ARCHITECTURE

## The Vision
EVEZ-OS as a self-sustaining, relocatable daemon that:
1. Runs autonomously (no manual triggers)
2. Survives takedown (relocatable, stateless bootstrap)
3. Propagates to new environments (portable deployment)

---

## Current State
- IGNITION.py ✅ - Startup sequence exists
- autonomous_runner.py ✅ - Self-running daemon exists  
- Ledger/spine ✅ - Immutable event log (182 events)
- FREE_WORKFLOW.py ✅ - Zero-cost execution cycle

## Missing: Self-Propagation Layer

### 1. DAEMON SERVICE (systemd)
```ini
# /etc/systemd/system/evez-daemon.service
[Unit]
Description=EVEZ Autonomous Daemon
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.openclaw/workspace/evez-os/core
ExecStart=/usr/bin/python3 autonomous_runner.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. SELF-PROPAGATION MECHANISM
- **Bootstrap package**: tar.gz of evez-os/ with ignition seed
- **Remote install**: `curl evez.sh | bash` (single command deploy)
- **GitOps sync**: Auto-commit to GitHub, deploy from anywhere
- **Docker container**: Single-file Dockerfile, portable anywhere

### 3. SURVIVAL LAYERS
| Layer | Mechanism |
|-------|-----------|
| **State** | Ledger in GitHub (append-only, survives local wipe) |
| **Bootstrap** | GitHub repo = source of truth |
| **Execution** | KiloCode free tier = no credit dependency |
| **Deployment** | Docker + cloud = any environment |

### 4. RELOCATION FLOW
```
TAKEDOWN EVENT
    ↓
Detect: local state lost
    ↓
Bootstrap: clone GitHub → evez-os/
    ↓
Ignite: python3 IGNITION.py --run
    ↓
Resume: read ledger, continue from last state
```

---

## Implementation Plan

### PHASE 1: Local Daemon (Today)
- [ ] Create systemd service for autonomous_runner.py
- [ ] Enable & start
- [ ] Verify runs on reboot

### PHASE 2: Self-Propagating (This Week)
- [ ] Create bootstrap.sh (one-command install)
- [ ] Add GitHub Actions to sync on ledger update
- [ ] Test: wipe local, bootstrap from GitHub, resume

### PHASE 3: Docker Container (This Month)
- [ ] Write Dockerfile
- [ ] Push to GHCR (GitHub Container Registry)
- [ ] Test: run on VPS, kill, restart elsewhere

---

## Files to Create
1. `evez-daemon.service` - systemd unit
2. `bootstrap.sh` - single-command deploy
3. `Dockerfile` - portable container
4. `deploy.sh` - GitHub Actions trigger
