# Cron Strategy - Queue Drain

## Pulse Schedule

```cron
*/10 * * * * cd /root/.openclaw/workspace && python3 evez-os/organism/pulse_a_explorer.py >> logs/pulse_a.log 2>&1
*/15 * * * * cd /root/.openclaw/workspace && python3 evez-os/organism/pulse_b_harvest.py >> logs/pulse_b.log 2>&1
*/30 * * * * cd /root/.openclaw/workspace && python3 evez-os/organism/pulse_c_critic.py >> logs/pulse_c.log 2>&1
```

## Queue Drain

```cron
*/10 * * * * : Drain queue/tasks.jsonl using provider_ladder.json
```

## Implementation

The organism pulses (A/B/C) handle queue draining automatically via the task queue schema in rate-limit-resilience.