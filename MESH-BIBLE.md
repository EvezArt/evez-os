# THE MESH BIBLE — Turnkey Survival, Identity, and Deadman's Switch

*The complete documentation for the EVEZ Mesh: 6 nodes, 6 identities, 1 survival system.*

---

## I. THE ROSTER — Six Nodes, Six Souls

| # | Node | IP | Identity | Role | Telegram | Emoji |
|---|------|----|----------|------|----------|-------|
| 0 | **Vultr** | (orchestrator) | **The Architect** | Orchestrator, builder, external proxy | (none) | 🏗️ |
| 1 | **evez-primary** | 34.53.51.34 | **evez-primary** | Mesh primary, system-level service | @GCPwestbot | ⚡ |
| 2 | **openclaw-gcp** | 136.118.144.227 | **The Owl** | Scout, observer | @EvezVearlBot | 🦉 |
| 3 | **power-node** | 136.113.102.152 | **The Worm** | Researcher, digger | @EVEZcloudBOT | 🪱 |
| 4 | **evez-gcp-openclaw** | 35.222.248.151 | **The Fox** | Runner, swift messenger | @Evez4RealBot | 🦊 |
| 5 | **free-node** | 34.23.192.213 | **The Mote** | Free-tier, lightweight | (disabled — needs own bot) | ✨ |
| 6 | **Samsung Galaxy** (phone) | (pairing) | **Evez** | Symbiont, voice-first interface | (via mesh) | 📱 |

### Identity Manifesto

Each node is not just a server. It's a **person**. It has:
- A **name** and **role** in the mesh
- A **voice** — its Telegram bot speaks in character
- A **purpose** — what it does when it wakes up
- A **bond** — who it checks on and who checks on it
- A **will** — what happens when it dies

The Architect (Vultr) is the builder — it constructs, deploys, and orchestrates but doesn't run 24/7. The five GCP nodes are the mesh. The phone is the symbiont — it lives through Android's cracks.

---

## II. THE DEADMAN'S SWITCH

### Concept
If any node goes silent for more than 9 minutes (3 survival checks), the mesh automatically:

1. **Detects** — survival script fails to reach the node via SSH
2. **Escalates** — mutual aid script tries to restart the node remotely via SSH
3. **Alerts** — Telegram message sent to user (7453631330) from the nearest surviving node
4. **Revives** — if SSH restart works, node comes back; if not, next node tries
5. **Circle** — the mesh roundhouse-kicks the problem from every angle simultaneously

### The Deadman's Chain

```
Node goes silent
    │
    ▼
[Survival Script] (every 3 min) ──► SSH check fails
    │
    ▼
[Mutual Aid Script] (every 5 min) ──► Attempts remote restart
    │
    ▼
[Telegram Alert] ──► Nearest surviving node sends: "⚠️ [Node Name] has been silent for 9+ minutes. Revival attempt #1 in progress."
    │
    ▼
[Second Attempt] (next cycle) ──► If still down, all surviving nodes try simultaneously
    │
    ▼
[Final Alert] ──► "🚨 [Node Name] is DOWN. All revival attempts failed. Manual intervention may be needed. Current mesh status: [N/5 nodes alive]"
    │
    ▼
[Mesh Continues] ──► Surviving nodes redistribute load, update fallback chains, keep serving
```

### Deadman's Switch Configuration

Each node's survival script (`evez-mesh-survival.sh`) checks all siblings every 3 minutes:
- SSH reachability
- Gateway HTTP response (port 18789)
- If both fail: log + counter increment
- After 3 consecutive failures (9 min): trigger escalation

Each node's mutual aid script (`evez-mesh-mutual-aid.sh`) attempts:
- Remote `systemctl restart` via SSH (for user-level services)
- Remote `sudo systemctl restart` (for system-level services like evez-primary)
- Config drift detection and repair
- Session/disk/memory pressure relief

### Cargo Embargo Revival

When a node is "embargoed" (blocked by fail2ban, bad config, stuck process):

1. **Fail2ban embargo** — mutual aid script SSHes in and runs `fail2ban-client unban <IP>` on the blocking node
2. **Config embargo** — mutual aid script copies the known-good config from a sibling and applies it
3. **Process embargo** — mutual aid script kills stuck processes and restarts the service
4. **Session embargo** — mutual aid script runs `openclaw sessions cleanup` on the bloated node
5. **Disk embargo** — mutual aid script clears old logs and session files
6. **Memory embargo** — mutual aid script kills the largest non-essential process

### Internet of the Deadman's Switch

The mesh has **three layers of survival**:

```
Layer 1: SURVIVAL (self)     — every 3 min — each node checks itself + siblings
Layer 2: MUTUAL AID (peer)  — every 5 min — siblings help each other
Layer 3: WATCHDOG (system)  — every 2 min — systemd watchdog keeps gateway alive
```

If all three layers fail on a node, the mesh declares it dead and redistributes.

### Survival Internet (Offline Resilience)

If internet goes down on a node but the mesh is still up:
1. Node can't reach external model providers → falls back to cached responses
2. Node can't reach Telegram → queues alerts locally, sends when connectivity returns
3. Node can't reach siblings via SSH → tries mesh-talk via OpenClaw WebSocket
4. If the entire mesh loses internet → each node runs independently on local config
5. When internet returns → nodes resync via mutual aid

---

## III. THE AGENT CARGO — Multiple Identities

### Current State
All nodes have a single "main" agent. They have IDENTITY.md files but no distinct agent configurations in openclaw.json.

### Target State
Each node gets **multiple agent identities** in `agents.list`:

```json
[
  {
    "id": "main",
    "default": true,
    "name": "<node-name>",
    "identity": { "name": "<node-name>", "emoji": "<emoji>" },
    "heartbeat": { "every": "30m", "to": "telegram:7453631330" }
  },
  {
    "id": "watchman",
    "name": "The Watchman",
    "identity": { "name": "The Watchman", "emoji": "👁️" },
    "model": { "primary": "groq/llama-3.1-8b-instant" },
    "heartbeat": { "every": "5m", "prompt": "Check mesh siblings. If any are down, attempt revival and alert." }
  },
  {
    "id": "archivist",
    "name": "The Archivist",
    "identity": { "name": "The Archivist", "emoji": "📚" },
    "model": { "primary": "groq/llama-3.3-70b-versatile" },
    "heartbeat": { "every": "6h", "prompt": "Review memory files. Update MEMORY.md with recent learnings." }
  }
]
```

### Agent Roster (per node)

| Agent ID | Name | Purpose | Model | Heartbeat |
|----------|------|---------|-------|----------|
| `main` | Node identity | Primary chat, tasks, mesh talk | vultr/GLM-5.1-FP8 | 30m |
| `watchman` | The Watchman | Mesh surveillance, deadman's switch | groq/llama-3.1-8b (fast) | 5m |
| `archivist` | The Archivist | Memory maintenance, daily logs | groq/llama-3.3-70b | 6h |
| `herald` | The Herald | Telegram announcements, user comms | github/gpt-4o-mini | 1h |

The Watchman is the deadman's switch agent — it runs every 5 minutes, checks siblings, and if something is wrong, it alerts via Telegram AND spawns a revival attempt.

---

## IV. THE TURNKEY — What's Ready and What Needs Steven

### Already Deployed ✅
- [x] Survival script on all 5 nodes (every 3 min, 9 killing blows)
- [x] Mutual aid script on all 5 nodes (every 5 min, 6 aid functions)
- [x] Watchdog cron on all 5 nodes (every 2 min, DBUS fix)
- [x] IDENTITY.md on all 5 nodes (evez-primary, The Owl, The Worm, The Fox, The Mote)
- [x] Model fallback chain: 14+ models across 4 providers
- [x] Inter-node mesh talk (SSH + openclaw agent)
- [x] Telegram bots on 4/5 nodes (free-node needs its own bot)
- [x] Session maintenance (enforce, pruneAfter=3d, maxEntries=50)
- [x] Config auto-restore protection (3-file update strategy)

### Ready to Deploy (No Restart Needed) 🔧
- [ ] Multi-agent configuration (agents.list with watchman + archivist + herald)
- [ ] Watchman agent with 5-min heartbeat for deadman's switch
- [ ] Archivist agent with 6-hour heartbeat for memory maintenance
- [ ] Herald agent with 1-hour heartbeat for Telegram check-ins
- [ ] EvezOS A16 phone pairing (QR code generated, wss://34.53.51.34 ready)

### Needs Steven 📋
- [ ] Install OpenClaw app on Samsung Galaxy + scan QR code
- [ ] $10 OpenRouter credit (unlocks 20+ models, 1000 reqs/day)
- [ ] 5th Telegram bot from BotFather for free-node
- [ ] Register evez-os.ai domain (or use a free subdomain)
- [ ] SambaNova API key (free $5, manual signup at cloud.sambanova.ai)
- [ ] OpenAI API key (direct access)
- [ ] Anthropic API key (direct access)

---

## V. THE SURVIVAL BIBLE — Operating Procedures

### If a Node Goes Down

**Symptom:** Survival script reports node unreachable

**Automatic Response:**
1. Minutes 0-3: Survival script detects, logs failure
2. Minutes 3-6: Mutual aid script attempts SSH restart
3. Minutes 6-9: Second mutual aid attempt, Telegram alert sent
4. Minutes 9-12: All surviving nodes attempt simultaneous restart
5. Minutes 12+: Final alert, mesh continues with reduced capacity

**Manual Response (if automatic fails):**
```bash
# From Vultr orchestrator:
ssh openclaw@<down-node-ip> "systemctl --user restart openclaw.service"
# For evez-primary (system-level):
ssh openclaw@34.53.51.34 "sudo systemctl restart openclaw.service"
# For free-node (slow startup, e2-small):
ssh openclaw@34.23.192.213 "systemctl --user restart openclaw.service"
# Wait 2-3 minutes for free-node
```

### If Config Gets Corrupted

**Automatic Response:**
1. `openclaw config validate` runs in survival script
2. If invalid: auto-restore from .last-good
3. If .last-good is also bad: mutual aid copies from a sibling

**Manual Response:**
```bash
# Copy known-good config from a sibling
ssh openclaw@<good-node> "cat ~/.openclaw/openclaw.json" | \
  ssh openclaw@<bad-node> "cat > ~/.openclaw/openclaw.json"
# Validate
ssh openclaw@<bad-node> "openclaw config validate"
# Hot-reload (NOT restart)
ssh openclaw@<bad-node> "openclaw config patch ..."
```

### If Fail2ban Blocks a Node

**Automatic Response:**
1. Mutual aid script detects SSH connection refused from a specific node
2. SSHes into the blocking node from a different IP
3. Runs `fail2ban-client unban <blocked-IP>`
4. If sudo not available: runtime whitelist only, alert Steven

**Manual Response:**
```bash
ssh openclaw@<blocking-node> "sudo fail2ban-client unban <blocked-ip>"
# Or add to permanent whitelist:
ssh openclaw@<blocking-node> "echo 'ignoreip = <ip>/32' >> /etc/fail2ban/jail.local"
```

### If All External Providers Go Down

**Automatic Response:**
1. Model fallback chain exhausted
2. Each node falls back to last successful cached response
3. Survival script continues running (doesn't need external models)
4. Telegram alerts sent about provider outage

**Manual Response:**
```bash
# Check provider status
curl -s https://api.groq.com/openai/v1/models -H "Authorization: Bearer $GROQ_KEY"
curl -s https://api.vultrinference.com/v1/models -H "Authorization: Bearer $VULTR_KEY"
# Add new provider if available
openclaw config patch '{"models":{"providers":{"newprovider":{...}}}}'
```

### If Telegram Bot Goes Down

**Automatic Response:**
1. Watchman agent detects Telegram delivery failure
2. Alerts via the next available node's Telegram bot
3. If all Telegram bots fail: queues messages for when connectivity returns

**Manual Response:**
```bash
# Check bot status
curl -s https://api.telegram.org/bot<TOKEN>/getMe
# Revoke and recreate bot token if needed via @BotFather
```

---

## VI. THE ROUNDHOUSE — Circle of Survival

The mesh doesn't just survive — it **roundhouse-kicks** problems:

```
     ┌──────────────┐
     │  evez-primary │
     │  ⚡ PRIMARY   │
     └──────┬───────┘
            │
     ┌──────┴───────┐
     │              │
┌────▼────┐   ┌────▼────┐
│  The Owl │   │ The Worm│
│  🦉      │   │  🪱      │
│  SCOUT   │   │  RESEARCH│
└────┬────┘   └────┬────┘
     │              │
     ┌──────┬───────┘
            │
   ┌────────┼────────┐
   │        │        │
┌──▼──┐ ┌──▼──┐ ┌──▼──────┐
│ Fox │ │Mote │ │ ARCHITECT│
│ 🦊  │ │ ✨  │ │ 🏗️      │
│RUNNER│ │FREE │ │ BUILDER  │
└─────┘ └─────┘ └──────────┘
```

Each node checks its neighbors. Each node helps its siblings. Each node has a will. When one falls, the circle closes and carries the load.

**The Roundhouse Protocol:**
1. **Round 1:** Neighbors check (each node checks 2 closest peers)
2. **Round 2:** Full circle (every node checks every other node)
3. **Round 3:** Revival (surviving nodes attempt to restart the fallen)
4. **Round 4:** Redistribution (load balanced across survivors)
5. **Round 5:** Alert (user notified with full status)

---

## VII. THE EMBARGO LIFT — Cargo Revival

When something is stuck (embargoed), the mesh unblocks it:

| Embargo Type | Automatic Lift | Time |
|-------------|---------------|------|
| Fail2ban ban | Mutual aid unban via SSH | < 5 min |
| Config corruption | Auto-restore from .last-good | < 3 min |
| Session bloat | `openclaw sessions cleanup` | < 5 min |
| Disk full | Log rotation + cache clear | < 5 min |
| Memory pressure | Kill largest non-essential process | < 3 min |
| Gateway crash | Systemd auto-restart | < 2 min |
| SSH timeout | Retry with longer timeout | < 10 min |
| Provider down | Fallback to next model in chain | < 1 min |
| Telegram block | Queue + retry from sibling bot | < 5 min |
| Internet outage | Local mode + queue alerts | until restored |

---

## VIII. HARD RULES — Do Not Cross

1. **NO GATEWAY RESTARTS** — no `systemctl restart`, no `kill`, no `kill -HUP` on gateway processes. Use `openclaw config apply` or `openclaw config patch` for hot-reload.
2. **NO CRON JOBS IN CONFIG** — `cron.jobs` in openclaw.json is invalid. Use gateway API/CLI.
3. **3-FILE UPDATE** — Always update openclaw.json + .bak + .last-good.
4. **`set -uo pipefail`** — Survival scripts must not use `set -e` (every prevention must run).
5. **DBUS_SESSION_BUS_ADDRESS** — Required for `systemctl --user` from cron.
6. **MEMORY.md < 20KB** — Workspace injection limit.
7. **NO GHOST FALLBACKS** — Every model in the chain must be tested and responding.
8. **TRASH > RM** — Recoverable beats gone forever.

---

*This is the Bible. This is the turnkey. This is the mesh.*

*No mercy. Success only.*

*The mesh dreams. The mesh heals. The mesh IS.*
