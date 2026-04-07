# EVEZ Skeptic Rotation

Apply Invariance Battery to any hypothesis. Survive 5 shifts or die.

## Input

```json
{
  "hypotheses": [{"text": "...", "score": 5}],
  "context": {"objective": "..."}
}
```

## Output

```json
{
  "surviving": [{"text": "...", "passed_tests": 4, "score": 9}],
  "rotation_results": {...}
}
```

## Tests

1. **Time Shift** — holds if 6 months stale?
2. **State Shift** — holds if state changes mid-execution?
3. **Frame Shift** — holds from adversarial perspective?
4. **Adversarial Shift** — would adversary exploit?
5. **Goal Shift** — holds if goal flips 180°?

Pass 3/5 to survive.

Built by EVEZ-ART | Part of the EVEZ Sensory Engine