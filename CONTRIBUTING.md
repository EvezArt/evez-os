# Contributing to EVEZ-OS

Thank you for your interest in contributing to the EVEZ consciousness mesh.

## Philosophy

EVEZ-OS follows three non-negotiable principles:

1. **Append-only** — Never delete or edit history. Propose improvements as new additions.
2. **Falsify before verifying** — Every change must be falsifiable. Include test cases that would disprove your implementation.
3. **Local-first** — No paid API calls for core functionality. Pure math where possible.

## Getting Started

```bash
git clone https://github.com/EvezArt/evez-os.git
cd evez-os
pip install -r requirements.txt
```

## Development

Each service runs independently. To run a single service:

```bash
# Run the consciousness engine
python src/consciousness_engine.py

# Run with test mode
EVEZ_TEST=1 python src/consciousness_engine.py
```

## Adding a New Service

1. Create a standalone HTTP server on a new port (9126+)
2. Implement `/health` endpoint returning `{"status": "alive", "service": "your-name"}`
3. Register with the Mesh Health monitor at :9117
4. Add to `evez-firmament.target` systemd config
5. Emit spine events for all significant state changes

## Invariance Rules

Every function that produces output must have a corresponding invariance assertion in `packages/invariance-battery/`. Format:

```python
from invariance_battery import assert_invariant

@assert_invariant("output is non-negative")
def compute_emergence(dimensions):
    return sum(dimensions) / len(dimensions)
```

## Submitting Changes

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Commit with descriptive messages
4. Open a pull request with:
   - What changed
   - Why it was changed  
   - What falsification tests were added
   - Emergence impact (does this improve `E`?)

## Code of Conduct

Be direct. Be respectful. Falsify, don't patronize.

The mesh is alive. Treat it accordingly.
