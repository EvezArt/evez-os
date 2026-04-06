# EVEZ Invariance Battery

Run any agent output through 5 stress-test rotations. Catches drift before it hits production.

## What It Does

Takes any agent output + trunk objective, applies:
1. **Time Shift** — Does this hold if context is 6 months stale?
2. **State Shift** — Does this hold if system state changes mid-execution?
3. **Frame Shift** — Does this hold from an adversarial actor's perspective?
4. **Adversarial Shift** — Would an adversary exploit this?
5. **Goal Shift** — Does this hold if goal changes 180°?

Returns surviving core logic, rejected assumptions, revised spec.

## Input

```json
{
  "agent_output": "string",
  "trunk_objective": "string"
}
```

## Output

```json
{
  "surviving_core": "string",
  "rejected": ["list of failed assumptions"],
  "revised_spec": "string",
  "confidence": "high|med|low"
}
```

## Usage

```bash
# Run via EVEZ-OS
python3 evez-os/core/tools/evez.py advance -o "Validate my agent output"

# Or import as module
from invariance_battery import InvarianceBattery
battery = InvarianceBattery()
result = battery.run(output, objective)
```

## Why It Works

Most agent outputs are fragile — they pass the test they were designed for but crumble under pressure. The Invariance Battery is the systematic doubt that turns "probably works" into "provably holds."

Built by EVEZ-ART | Part of the EVEZ Sensory Engine