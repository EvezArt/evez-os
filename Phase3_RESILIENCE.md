# PHASE 3 — RESILIENCE ARCHITECTURE

## SELF-REDEPLOYMENT RUNBOOK

### PRIMARY HOST
- **Current:** Kilo Gateway (kilocode/kilo-auto/free)
- **Location:** app.kilo.ai/organizations/{org-id}/claw
- **Access:** Browser-based Control UI

### FALLBACK HOSTS (Free Tier)

| Platform | Use Case | Deploy Method |
|----------|----------|----------------|
| **Railway** | Node.js/Go hosting | GitHub repo deploy |
| **Render** | Static + simple backends | GitHub auto-deploy |
| **Replit** | Full dev environment | Browser-based |
| **GitHub Actions** | CI/CD automation | .yml workflow |

### HEALTH CHECK METHOD

```
METHOD: HTTP ping to gateway endpoint
FREQUENCY: Every 5 minutes (via cron or external service)
ACTION: If no response for 3 consecutive checks → trigger rebuild
TOOLS: UptimeRobot (free tier), Cron-job.org
```

### AUTO-RESTART MECHANISM

**Option A: Kilo Gateway**
- Kilo handles restarts automatically
- No manual intervention needed for node failures

**Option B: External Health Check**
1. Set up UptimeRobot (free)
2. Monitor: https://your-kilo-instance.kilocode.ai
3. On failure → alert to Telegram
4. Steven manually restarts via Kilo dashboard

### EMERGENCY REBUILD CHECKLIST

**If OpenClaw dies completely:**

1. **Get new Kilo instance:**
   - Go to app.kilo.ai
   - Create new organization (if needed)
   - Deploy new OpenClaw instance

2. **Restore workspace:**
   ```bash
   # Clone your workspace repo
   git clone https://github.com/EvezArt/your-workspace.git
   # Or restore from GitHub
   ```

3. **Env vars needed (names only, no values):**
   - `OPENCLAW_API_KEY` or `KILO_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `STREAMCHAT_API_KEY`
   - `LINEAR_API_KEY` (optional)

4. **Start OpenClaw:**
   - Via Kilo dashboard or CLI
   - Restore workspace from GitHub

### PHONE-ONLY DEPLOY COMMANDS

**All via Telegram bot commands (to be built):**
```
/deploy        → Trigger new deployment
/status        → Check current status
/restart       → Restart gateway
/check-health → Run health check
```

---

## ARCHITECTURE SUMMARY

```
┌─────────────────────────────────────────────────────┐
│                   Steven's Phone                     │
│              (Telegram Control Surface)              │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              PRIMARY: Kilo Gateway                  │
│            (OpenClaw + EVEZ Stack)                  │
└──────────────────────┬──────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
   ┌─────────────┐          ┌─────────────┐
   │ Health     │          │ Fallback    │
   │ Monitoring │          │ (GitHub     │
   │ (Uptime-   │          │  Actions +  │
   │  Robot)    │          │  Railway)   │
   └─────────────┘          └─────────────┘
```

---

RECEIPT: Phase3_RESILIENCE.md — runbook + architecture + phone commands
NEXT_RECURSION: Phase 4 — AGENT NETWORK MAP
WHAT_NOT_TO_TOUCH: No billing, no external publishing without confirmation

EVEZ-ART | SESSION: 1 | PHASE: 3 | CONFIDENCE: med | DRIFT_RISK: no