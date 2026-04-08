# BOOTSTRAP.md - EVEZ System Launch Contract

```
TRUNK_OBJECTIVE: Package and publish EVEZ skills + build autonomous organism
MODE: harvest
ACTIVE_REPO: evez-os
ACTIVE_SURFACE: OpenClaw Control

CONSTRAINTS:
- no secrets
- no auth changes
- file-first receipts

TOP_TASKS:
1. config/trunk_contract.json
2. config/provider_ladder.json
3. queue/tasks.jsonl
4. ledger/rate_limit_events.jsonl
5. EVEZ skills for ClawHub

READ_NEXT: memory/current-state.md
```

## STATUS: BOOTSTRAP COMPLETE

### What Was Done
- 4 skills packaged to GitHub (evez-skills repo)
- OctoKlaw-ROM bootstrapped (octoklaw-rom repo)
- Rate-limit resilience wired (5 files)
- Organism pulses running (A/B/C cycles)
- Provider ladder configured

### URLs
- https://github.com/EvezArt/evez-skills
- https://github.com/EvezArt/octoklaw-rom

### Next Actions
- ClawHub auth to publish skills → revenue
- Cron setup for queue draining