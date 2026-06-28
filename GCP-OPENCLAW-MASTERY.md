# GCP + OpenClaw Mastery Guide
## From Newbie to Luxury-Grade Autonomous Operator

*The cube has six faces. This guide has six phases. Each face is a discipline.*

---

## PHASE 1: GCP Foundations (The Ground)

### What GCP Actually Is
Google Cloud Platform = rented computers in Google's data centers. You pay for what you use. No upfront cost. You get:
- **VMs** (Compute Engine) — full Linux boxes you control
- **Networking** — firewalls, IP addresses, routing
- **Storage** — disks, buckets
- **IAM** — who can do what

### Your Current Mesh (Already Built)
```
Project: evez666
Account: evez-os@evez666.iam.gserviceaccount.com

5 Instances:
┌─────────────────────┬───────────────┬──────────────┬─────────────┐
│ Name                │ Zone           │ Machine Type │ External IP │
├─────────────────────┼───────────────┼──────────────┼─────────────┤
│ evez-primary        │ us-west1-b     │ e2-standard-2│ 34.53.51.34 │
│ openclaw-gcp        │ us-west1-b     │ e2-medium    │ 136.118.144.227 │
│ evez-gcp-openclaw   │ us-central1-a  │ e2-medium    │ 35.222.248.151 │
│ openclaw-power-node │ us-central1-a  │ e2-medium    │ 136.113.102.152 │
│ evez-free-node      │ us-east1-b     │ e2-small     │ 34.23.192.213 │
└─────────────────────┴───────────────┴──────────────┴─────────────┘
```

### Essential GCP Commands You'll Use Daily

```bash
# See your instances
gcloud compute instances list

# SSH into any node
gcloud compute ssh evez-primary --zone us-west1-b

# Start/stop instances (saves money)
gcloud compute instances stop evez-free-node --zone us-east1-b
gcloud compute instances start evez-free-node --zone us-east1-b

# Create a new node
gcloud compute instances create NEW-NAME \
  --zone us-west1-b \
  --machine-type e2-small \
  --image-family ubuntu-2204-lts \
  --image-project ubuntu-os-cloud \
  --boot-disk-size 30GB

# Open a firewall port
gcloud compute firewall-rules create openclaw-gateway \
  --allow tcp:18789 \
  --source-ranges 0.0.0.0/0 \
  --description "OpenClaw gateway port"

# See your project config
gcloud config list

# See billing (IMPORTANT - don't surprise yourself)
gcloud billing projects describe evez666
```

### Machine Types Decoded
- **e2-small** (2GB RAM, 0.25 vCPU) — $8/mo — lightweight tasks
- **e2-medium** (4GB RAM, 0.5 vCPU) — $13/mo — solid for OpenClaw
- **e2-standard-2** (8GB RAM, 2 vCPU) — $25/mo — primary node, heavy work
- **e2-standard-4** (16GB RAM, 4 vCPU) — $50/mo — if you need real power

### Zones
- **us-west1-b** — Oregon (your primary + openclaw-gcp are here)
- **us-central1-a** — Iowa (power-node + openclaw-openclaw)
- **us-east1-b** — South Carolina (free-node)
- Pick zones close to you for lower latency

---

## PHASE 2: OpenClaw Architecture (The Structure)

### What OpenClaw Actually Is
OpenClaw is a **personal AI agent gateway**. It runs on your server, connects to AI models, and lets you talk to them through Telegram, WhatsApp, Discord, web chat, and more. Think of it as:
- A router (sends messages to AI models)
- A memory system (remembers conversations across sessions)
- A tool platform (AI can run commands, browse, code)
- A mesh coordinator (multiple nodes can work together)

### The Key Components
```
~/.openclaw/
├── openclaw.json          ← THE config (models, channels, plugins)
├── openclaw.json.bak      ← Backup (always keep in sync)
├── openclaw.json.last-good← Last validated config
├── workspace/            ← Your agent's home
│   ├── AGENTS.md          ← How the agent behaves
│   ├── SOUL.md            ← Personality/voice
│   ├── MEMORY.md          ← Long-term memory
│   ├── TOOLS.md           ← Local tool notes
│   ├── USER.md            ← About you (Steven)
│   ├── HEARTBEAT.md       ← Periodic check config
│   └── memory/            ← Daily memory files
└── paired.json           ← Paired device info (phone)
```

### The Gateway
The **gateway** is the process that runs OpenClaw. It:
- Listens on port 18789 (HTTP) for the Control UI
- Routes messages to/from channels (Telegram, WhatsApp, etc.)
- Talks to AI model providers (Groq, Google, GitHub, Vultr, etc.)
- Runs tools (exec, file operations, browser, etc.)
- Manages sessions and memory

```bash
# Start the gateway
openclaw gateway start

# Check status
openclaw status

# Restart (after config changes)
openclaw gateway restart

# Validate config BEFORE restart
openclaw config validate

# Fix common issues
openclaw doctor --fix
```

### Systemd Service (The Autonomic Part)
Your nodes use systemd to keep OpenClaw alive automatically:
```bash
# User-level service (most nodes)
systemctl --user status openclaw-gateway.service
systemctl --user restart openclaw-gateway.service

# System-level service (evez-primary)
sudo systemctl status openclaw.service
sudo systemctl restart openclaw.service

# Check logs
journalctl --user -u openclaw-gateway.service -n 50 --no-pager
```

---

## PHASE 3: Model Configuration (The Voice)

### How Models Work in OpenClaw
Your config (`openclaw.json`) defines:
1. **Providers** — where the AI models live (Vultr, Groq, Google, GitHub, etc.)
2. **Models** — specific AI models under each provider
3. **Primary** — the default model used for new conversations
4. **Fallbacks** — if the primary fails, try these in order

### Your Current Model Chain (41 models, 9 providers)
```json
{
  "models": {
    "providers": {
      "vultr": {
        "baseUrl": "https://api.vultrinference.com/v1",
        "apiKey": "YOUR_KEY",
        "auth": "token",
        "models": [
          {"id": "zai-org/GLM-5.1-FP8", "name": "GLM-5.1"},
          {"id": "deepseek-ai/DeepSeek-V4-Flash"},
          {"id": "nvidia/DeepSeek-V3.2-NVFP4"},
          // ... 10 models total
        ]
      },
      "groq": {
        "baseUrl": "https://api.groq.com/openai/v1",
        "apiKey": "YOUR_KEY",
        "models": [
          {"id": "llama-3.3-70b-versatile"},
          {"id": "llama-3.1-8b-instant"},
          {"id": "openai/gpt-oss-120b"}
        ]
      }
      // ... google, github, openrouter, cohere, ollama
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "vultr/zai-org/GLM-5.1-FP8",
        "fallbacks": [
          "groq/llama-3.3-70b-versatile",
          "groq/openai/gpt-oss-120b",
          "google/gemini-2.5-flash",
          // ... 30+ more
        ]
      }
    }
  }
}
```

### Model Test Results (2026-06-28)
**15 ALIVE / 47 TOTAL**

✅ **Working Providers:**
- **Groq** (3/3 alive) — Fast, free, reliable. 0.7s response time.
- **GitHub** (2/3 alive) — gpt-4o + gpt-4o-mini work. 405b-instruct down.
- **Vultr** (2/10 alive) — Only DeepSeek-V4-Flash + DeepSeek-V3.2-NVFP4 respond.
- **OpenRouter** (6/12 alive) — Free tier works for gemma + nemotron + liquid models.
- **Google** (1/7 alive) — Only gemini-2.5-flash via google-generative-ai API works.

❌ **Dead Providers:**
- **HuggingFace** — Connection refused (all 3 models)
- **Cohere** — HTTP 405 (wrong API format)
- **Ollama** — Timed out (CPU-only, too slow on these nodes)

### Adding a New Provider
```bash
# Via CLI
openclaw config set models.providers.NEWPROVIDER '{"baseUrl":"https://api.example.com/v1","apiKey":"YOUR_KEY","auth":"token","api":"openai-completions","models":[{"id":"model-name","name":"Display Name"}]}' --strict-json

# Via direct edit (then validate)
# Edit ~/.openclaw/openclaw.json
# Add to models.providers section
openclaw config validate
```

### Getting API Keys
| Provider | Free Tier | Get Key |
|----------|----------|---------|
| Groq | Yes, unlimited-ish | console.groq.com/keys |
| Google AI | Yes, quota-limited | aistudio.google.com/apikey |
| GitHub Models | Yes (with GitHub account) | github.com/settings/tokens |
| OpenRouter | Free models available | openrouter.ai/keys |
| Vultr | Included with account | my.vultr.com/settings/api |
| Cohere | Trial keys | dashboard.cohere.com/api-keys |

---

## PHASE 4: Channels & Communication (The Signal)

### Telegram Setup (Already Done on All Nodes)
```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "allowlist",
      "allowFrom": ["tg:YOUR_CHAT_ID"]
    }
  }
}
```

**To add a new Telegram bot:**
1. Talk to @BotFather on Telegram → `/newbot` → get token
2. Add to config under `channels.telegram.botToken`
3. Set `allowFrom` with your Telegram user ID
4. Restart gateway

### Other Channels
- **WhatsApp** — Scan QR code, link phone
- **Discord** — Create bot at discord.com/developers
- **Signal** — Via signal-cli
- **Web Chat** — Built into the gateway at http://YOUR_IP:18789/

---

## PHASE 5: Automation & Self-Healing (The Autonomic Nervous System)

### Cron Jobs (Scheduled Tasks)
Your nodes have cron jobs that check health and restart services:
```bash
# View cron
crontab -l

# Edit cron
crontab -e

# Typical watchdog entry (checks every 2-3 min)
*/3 * * * * /home/openclaw/health-check.sh >> /home/openclaw/health.log 2>&1
```

### Systemd Restart Policies
```ini
# In service file: Restart=always means if it dies, it comes back
[Service]
Restart=always
RestartSec=5
```

### Defense in Depth (Your Current Setup)
1. **systemd** — Restart=always (instant restart on crash)
2. **Cron watchdog** — Checks every 2-3 min, restarts if down
3. **@reboot** — Gateway starts on boot
4. **Peer-watch** — Nodes watch each other in a circle
5. **Deadman's switch** — evez-primary watches all 4 peers

### Heartbeat System
The heartbeat is a periodic check-in where the agent can:
- Check emails, calendar, weather
- Monitor mesh health
- Do background maintenance
- Proactively message you if something's wrong

Configured in `HEARTBEAT.md` and `openclaw.json`:
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m"
      }
    }
  }
}
```

---

## PHASE 6: Luxury-Grade Operations (The Apex)

### Daily Operations Checklist

**Checking mesh health:**
```bash
# All gateways
for ip in 34.53.51.34 34.23.192.213 35.222.248.151 136.113.102.152 136.118.144.227; do
  echo -n "$ip: "
  curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://$ip:18789/
  echo
 done

# All API endpoints
for ip in 34.53.51.34 34.23.192.213 35.222.248.151 136.113.102.152 136.118.144.227; do
  echo -n "$ip:18790: "
  curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://$ip:18790/api/status
  echo
 done
```

**Testing models:**
```bash
# Quick test via OpenClaw
# Just send a message in web chat or Telegram — if you get a reply, the model chain works

# Deep test (all models)
# Run the test script we built today
python3 /tmp/test_all_models2.py
```

**Config changes (THE safe workflow):**
```bash
# 1. Always validate first
openclaw config validate

# 2. If valid, restart gateway (or it hot-reloads)
openclaw gateway restart

# 3. If invalid, fix or restore
openclaw doctor --fix

# GOLDEN RULE: Always update .bak AND .last-good when editing manually
```

### SSH Key Management
```bash
# Your SSH keys let nodes talk to each other
ls ~/.ssh/
# id_ed25519 = your private key (NEVER share)
# id_ed25519.pub = your public key (put on other nodes)

# Add key to a node
ssh-copy-id user@ip_address

# SSH into a GCP node
gcloud compute ssh NODE_NAME --zone ZONE
# OR
ssh user@EXTERNAL_IP
```

### Adding a New Node to the Mesh
```bash
# 1. Create GCP instance
gcloud compute instances create NEW-NODE \
  --zone us-west1-b \
  --machine-type e2-medium \
  --image-family ubuntu-2204-lts \
  --image-project ubuntu-os-cloud \
  --boot-disk-size 30GB

# 2. SSH in and install OpenClaw
sudo npm install -g openclaw@latest

# 3. Copy config from existing node
scp ~/.openclaw/openclaw.json NEW_IP:~/.openclaw/
scp -r ~/.openclaw/workspace/* NEW_IP:~/.openclaw/workspace/

# 4. Set up systemd service
# 5. Open firewall ports (18789, 18790, 11434)
# 6. Create Telegram bot for the node
# 7. Start gateway
```

### The 10 Commandments of Luxury-Grade Operations

1. **Validate before restart** — `openclaw config validate` ALWAYS
2. **Three-file sync** — Update openclaw.json + .bak + .last-good together
3. **trash > rm** — Never delete what you can't recover
4. **Test models after config changes** — Send a message, confirm a reply
5. **Monitor disk space** — `df -h` — Ollama models eat disk fast
6. **Keep API keys fresh** — Rotate every 90 days
7. **Document everything** — MEMORY.md is your continuity
8. **One change at a time** — Don't edit 5 things then debug
9. **Read the error** — The error message tells you what's wrong. Read it.
10. **The mesh heals** — If one node dies, the others catch it. Trust the system.

### Your Mesh Right Now
```
       ┌─────────────────┐
       │   VULTR (Orch)  │ ← Orchestrator only, no content
       │  207.148.12.53  │
       └────────┬────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼───┐  ┌───▼───┐  ┌───▼───┐
│PRIMARY│  │ POWER │  │OPENCLW│
│west1b│  │cent1a │  │cent1a │
└───┬───┘  └───────┘  └───────┘
    │
┌───▼───┐  ┌───────┐
│ SMALL│  │  KNOT │
│east1b│  │ west1b│
└───────┘  └───────┘
```

5 GCP nodes + 1 Vultr orchestrator = 6-node mesh
All gateways: HTTP 200 ✓
All API endpoints: HTTP 200 ✓
Deadman's switch: Active ✓
Circular peer-watch: Active ✓

---

## QUICK REFERENCE CARD

| Task | Command |
|------|---------|
| Check mesh | `curl` each IP:18789 |
| Check models | Send a test message |
| Edit config | `openclaw config set <path> <value>` |
| Validate config | `openclaw config validate` |
| Fix config | `openclaw doctor --fix` |
| Restart gateway | `openclaw gateway restart` |
| View logs | `openclaw logs` or `journalctl --user -u openclaw-gateway.service` |
| Check GCP | `gcloud compute instances list` |
| SSH to node | `gcloud compute ssh NODE --zone ZONE` |
| Stop a node | `gcloud compute instances stop NODE --zone ZONE` |
| Ollama models | `curl http://127.0.0.1:11434/api/tags` |
| Telegram test | Send message to bot |
| Disk check | `df -h` |
| Memory check | `free -h` |
| Process check | `ps aux \| grep openclaw` |
| Cron check | `crontab -l` |

---

*The cube has six faces. The operator has six disciplines. The mesh is alive. The prophecy fulfills itself.*

⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⥋

*Built 2026-06-28 by The Architect for Steven Crawford-Maggard (EVEZ666)*
