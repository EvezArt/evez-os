# PHASE 5 — TELEGRAM CONTROL SURFACE

## COMMAND SET FOR STEVEN'S PHONE

### CORE COMMANDS (Must Have)

| Command | Action | Triggered Behavior |
|---------|--------|-------------------|
| `/start` | Welcome | Show available commands |
| `/status` | Check system | Return: uptime, active repos, revenue, health |
| `/deploy` | Deploy to new host | Clone workspace + start OpenClaw (via GitHub Actions) |
| `/restart` | Restart gateway | Trigger gateway restart |
| `/check-income` | Revenue check | Return: revenue_log.jsonl summary |

### SHIPPING COMMANDS

| Command | Action | Triggered Behavior |
|---------|--------|-------------------|
| `/ship` | Ship to Gumroad | Return: product upload links (Steven clicks) |
| `/x-post` | Post to X | Return: next scheduled post (needs auth first) |
| `/products` | List products | Return: active products with links |

### AGENT COMMANDS

| Command | Action | Triggered Behavior |
|---------|--------|-------------------|
| `/run [agent]` | Run specific agent | Execute evez-os agent (e.g., /run revenue) |
| `/scan` | Scan repos | Return: REPO ARBITER output |
| `/health` | System health | Return: gateway + tools status |

### EMERGENCY COMMANDS

| Command | Action | Triggered Behavior |
|---------|--------|-------------------|
| `/rebuild` | Emergency rebuild | Return: rebuild checklist from Phase 3 |
| `/help` | Get help | Show all commands |

### NOTIFICATIONS (Auto-triggered)

| Trigger | Message |
|---------|---------|
| Revenue received | "💰 New sale: $X for [PRODUCT]" |
| Gateway down | "⚠️ Gateway unreachable" |
| Health check fail | "🚨 Health check failed: [details]" |

---

## IMPLEMENTATION NOTES

**Current State:**
- Telegram bot is configured (token present in config)
- DM policy: pairing
- Need to add command handler logic

**Implementation Path:**
1. Add Telegram bot command handlers
2. Wire to OpenClaw exec + message tools
3. Test from Steven's phone

**Steven's Workflow:**
1. Open Telegram → @KiloClaw_bot
2. Type `/status` → Get system state
3. Type `/products` → See what's for sale
4. Type `/rebuild` → Get emergency steps

---

## COMMAND REFERENCE CARD

```
/start     → Welcome & commands
/status    → System status
/deploy    → Deploy new instance
/restart   → Restart gateway
/check-income → Revenue summary

/ship      → Product links
/x-post    → Next X post
/products  → Active products

/run [name] → Run agent
/scan      → Repo status
/health    → Health check

/rebuild   → Emergency rebuild
/help      → Command list
```

---

RECEIPT: Phase5_TELEGRAM.md — complete command set + reference card
NEXT_RECURSION: Phase 6 — HYPERAGENT SELF-MUTATION
WHAT_NOT_TO_TOUCH: No billing, no credentials

EVEZ-ART | SESSION: 1 | PHASE: 5 | CONFIDENCE: med | DRIFT_RISK: no