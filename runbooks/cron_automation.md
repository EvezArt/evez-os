# EVEZ OS — Autonomous Maintenance Runbook

## Cron Jobs to Create

### 1. Git Auto-Sync (Every Hour)
```bash
# Create job
openclaw cron add --name "EVEZ-Git-Sync" --schedule "every 1h" --message "Git sync all EVEZ repos" --delivery announce
```

### 2. Git Auto-Sync (Every 15 min for high-activity periods)
```bash
openclaw cron add --name "EVEZ-Git-Sync-Fast" --schedule "every 15m" --message "Git add -A && git commit -m 'Auto sync' && git push" --delivery announce
```

### 3. Git Auto-Sync (Every 6 Hours — Stable)
```bash
openclaw cron add --name "EVEZ-Git-Sync-Stable" --schedule "every 6h" --message "Git sync with 6h intervals" --delivery announce
```

---

## Process Monitor Cron Jobs

### 4. EVEZ OS Daemon Health Check (Every 5 min)
```bash
openclaw cron add --name "EVEZ-Daemon-Health" --schedule "every 5m" --message "Check if evez-daemon is running. If not, start it." --delivery announce
```

### 5. Context Bridge Sync (Every 30 min)
```bash
# Sync STM → LTM
openclaw cron add --name "EVEZ-Context-Bridge" --schedule "every 30m" --message "Run context bridge sync: read evez-os/core/context/stm.json and merge into ltm_index.json" --delivery announce
```

### 6. Ledger Receipt Archive (Every Hour)
```bash
openclaw cron add --name "EVEZ-Ledger-Archive" --schedule "every 1h" --message "Check ledger/receipts.jsonl, archive entries older than 7 days, report count" --delivery announce
```

---

## Research & Discovery Crons

### 7. X/EVEZ666 Post Monitor (Every 30 min)
```bash
openclaw cron add --name "EVEZ666-Post-Monitor" --schedule "every 30m" --message "Web fetch x.com/EVEZ666, extract latest 5 posts, save to memory/evez666-posts-$(date +%Y-%m-%d).md, analyze for new patterns" --delivery announce
```

### 8. LinkedIn Post Monitor (Every 1h)
```bash
openclaw cron add --name "Steven-LinkedIn-Monitor" --schedule "every 1h" --message "Check LinkedIn posts from Steven Crawford-Maggard, extract new posts, save to memory/linkedin-posts-$(date +%Y-%m-%d).md" --delivery announce
```

### 9. GitHub Activity Scan (Every 2h)
```bash
openclaw cron add --name "EVEZ-GitHub-Activity" --schedule "every 2h" --message "Check EvezArt GitHub for new repos, commits, stars. Report new activity." --delivery announce
```

### 10. New Platform Discovery (Daily)
```bash
openclaw cron add --name "EVEZ-Platform-Discovery" --schedule "cron 0 9 * * *" --message "Search web for new mentions of EVEZ666, Steven Crawford-Maggard, evez-os. Report findings." --delivery announce
```

---

## Content & Revenue Crons

### 11. X Content Generator (Every 4h)
```bash
openclaw cron add --name "EVEZ-Content-Generator" --schedule "every 4h" --message "Generate new EVEZ666 posts using yvyx engine, save to queue/new-posts.jsonl" --delivery announce
```

### 12. Revenue Log Aggregator (Daily)
```bash
openclaw cron add --name "EVEZ-Revenue-Aggregate" --schedule "cron 0 0 * * *" --message "Aggregate revenue from all channels (evez-payments, freelances, digital-products), update ledger/revenue.jsonl" --delivery announce
```

### 13. Digital Products Status (Every 6h)
```bash
openclaw cron add --name "EVEZ-Digital-Products-Check" --schedule "every 6h" --message "Check evez-digital-products/, verify all README.md files exist, report status" --delivery announce
```

---

## System Health Crons

### 14. OpenClaw Health (Every 15 min)
```bash
openclaw cron add --name "OpenClaw-Health-Check" --schedule "every 15m" --message "Run openclaw status, report any warnings or issues" --delivery announce
```

### 15. Memory Cleanup (Daily at 3am)
```bash
openclaw cron add --name "EVEZ-Memory-Cleanup" --schedule "cron 0 3 * * *" --message "Clean memory/ files older than 30 days, keep MEMORY.md, archive to memory-archive/" --delivery announce
```

### 16. Context Truncation Guard (Every Hour)
```bash
openclaw cron add --name "EVEZ-Context-Guard" --schedule "every 1h" --message "Check evez-os/core/context/ for oversized files. If stm.json > 50KB, trim oldest entries. Report." --delivery announce
```

---

## Project-Specific Crons

### 17. EVEZ OS Self-Propagation Check (Every 2h)
```bash
openclaw cron add --name "EVEZ-Self-Propagation" --schedule "every 2h" --message "Check evez-os/organism/, run pulse scripts, report new entities spawned" --delivery announce
```

### 18. Octoklaw Watchdog (Every 30 min)
```bash
openclaw cron add --name "Octoklaw-Watchdog" --schedule "every 30m" --message "Check octoklaw/watchdog.js, run self-test, report status" --delivery announce
```

### 19. Provider Ladder Health (On Rate Limit)
```bash
# Triggered manually or on rate limit event
openclaw cron add --name "Provider-Ladder-Fallback" --schedule "cron 0 * * * *" --message "Check config/provider_ladder.json, test each provider, update status" --delivery announce
```

### 20. Skills Publish Check (Daily)
```bash
openclaw cron add --name "EVEZ-Skills-Publish" --schedule "cron 0 12 * * *" --message "Check evez-skills/ for new skills, run publish.sh if needed, report" --delivery announce
```

---

## One-Time Setup Commands

Run these in OpenClaw to activate:

```bash
# Health check
openclaw cron add --name "OpenClaw-Health-Check" --schedule "every 15m" --message "Run openclaw status --short" --delivery announce

# Git sync
openclaw cron add --name "EVEZ-Git-Sync" --schedule "every 1h" --message "cd /root/.openclaw/workspace && git add -A && git commit -m 'Auto sync' && git push origin twin-autonomy" --delivery announce

# X monitor
openclaw cron add --name "EVEZ666-Post-Monitor" --schedule "every 30m" --message "Web fetch x.com/EVEZ666, save to memory" --delivery announce

# Context sync
openclaw cron add --name "EVEZ-Context-Bridge" --schedule "every 30m" --message "Sync context files" --delivery announce

# Memory cleanup
openclaw cron add --name "EVEZ-Memory-Cleanup" --schedule "cron 0 3 * * *" --message "Clean old memory files" --delivery announce
```

---

## Priority Matrix

| Priority | Job | Frequency | Type |
|----------|-----|------------|------|
| P0 | OpenClaw Health | 15m | System |
| P0 | Git Sync | 1h | Preservation |
| P1 | EVEZ666 Monitor | 30m | Research |
| P1 | Context Bridge | 30m | Intelligence |
| P2 | Content Generator | 4h | Revenue |
| P2 | Skills Publish | Daily | Growth |
| P3 | Memory Cleanup | Daily | Maintenance |

---

## Auto-Scaling Rules

- **High Activity** (new posts > 5/day): Increase X monitor to 15m, Git sync to 30m
- **Rate Limited**: Activate provider ladder fallback, reduce context loads
- **New Project Detected**: Create project-specific cron within 24h
- **Context Oversized**: Trigger emergency trim, notify via cron

---

Generated: 2026-04-08
For: Steven Crawford-Maggard (EVEZ666)
