# Rate-Aware Cron Strategy

## Pulse Pattern

Instead of long uninterrupted sessions, use **pulsed execution**:

| Pulse | Frequency | Duration | Work |
|-------|-----------|----------|------|
| Pulse A (Explore) | Every 15 min | ~30 sec | Generate hypotheses |
| Pulse B (Harvest) | Every 30 min | ~30 sec | Convert to revenue actions |
| Pulse C (Critic) | Every 60 min | ~30 sec | Log learnings |

## Context Budgeting Per Pulse

- **Pulse A**: 4k tokens max (small exploration)
- **Pulse B**: 6k tokens (action generation)
- **Pulse C**: 2k tokens (logging only)

## Rate Limit Response Flow

```
1. Request hits rate limit
   ↓
2. Classify task (critical/standard/background)
   ↓
3. If critical → wait and retry primary (max 2 tries)
   If standard → switch to fallback_tier_1
   If background → switch to fallback_tier_3 or queue
   ↓
4. If all exhausted → write to task_queue.jsonl
   ↓
5. Continue with next available task
```

## Queue Processing

Run queue drain on every 3rd Pulse A:

```bash
# In cron: every 45 minutes
*/45 * * * * cd /workspace && python3 drain_queue.py
```

Drain priority: critical → standard → background

## Monitoring

Track in `rate_limit_log.jsonl`:
- Events per hour
- Provider success rates
- Queue depth

## Emergency阀值

If queue depth > 20 or critical tasks blocked > 3:
- Alert operator via Telegram
- Pause Pulse A, continue only Pulse B for revenue

## Free-Tier Optimization

- Reserve primary for: final artifacts, architecture, code diffs
- Use fallback for: summaries, drafts, batch work
- Defer to cron for: logging, tagging, cache updates