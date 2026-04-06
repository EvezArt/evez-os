# EVEZ Hyperagent Loop

Meta-improvement cycle. Improve the agent that solves the task.

## Input

```json
{
  "task": "string",
  "iterations": 3
}
```

## Output

```json
{
  "final_agent_spec": "...",
  "delta_from_original": "...",
  "performance_gain_est": "..."
}
```

## Process

1. Execute task
2. Identify bottleneck
3. Propose one prompt/routing modification
4. Apply it
5. Re-run
6. Repeat N times

## Returns

- Final improved agent spec
- What changed from original
- Estimated performance gain

Built by EVEZ-ART | Part of the EVEZ Sensory Engine