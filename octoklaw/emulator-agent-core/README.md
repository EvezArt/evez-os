# OctoKlaw-ROM Emulator Agent Core

## Overview

The emulator core is the heart of OctoKlaw-ROM — a self-bootstrapping recursive agentic emulator organism. It runs a Playwright browser agent inside a JSON-defined ROM, logs every state-action-reward triple, and saves state on every decision point.

## Files

| File | Purpose |
|------|---------|
| `index.js` | Main emulator loop — loads ROM, runs agent, logs, saves |
| `rom-loader.js` | Validates and parses ROM JSON schema |
| `browser-agent.js` | Playwright agent — reads DOM, maps to world_state, executes actions |
| `save-state.js` | Writes checkpoints to /saves/gen-{n}.json and commits to git |

## Usage

### From Replit (Phone-friendly)

1. Create a new Replit (Node.js)
2. Copy these files
3. Add `playwright` dependency: `npm i playwright`
4. Run: `node index.js <rom-path>`

### CLI Options

```bash
# Run a specific ROM
node emulator-agent-core/index.js roms/rom-00-bootstrap.json

# Validate a ROM
node emulator-agent-core/rom-loader.js roms/rom-00-bootstrap.json

# List saved checkpoints
node emulator-agent-core/save-state.js list

# Load a generation
node emulator-agent-core/save-state.js load 0
```

## ROM Structure

A ROM is a JSON file containing:

```json
{
  "world_state": { "name": "...", "description": "..." },
  "action_space": [{ "type": "click", "params": { "selector": "..." } }],
  "reward_signal": { "type": "linear", "weights": {} },
  "terminal_condition": { "max_iterations": 1000 },
  "generation_meta": { "generation": 0 }
}
```

## State-Action-Reward Logging

Every iteration logs:
- Current world state
- Selected action
- Received reward
- Timestamp

These triples form the learning history that drives the ROM builder's pattern compression.

## Save States

Checkpoints written to:
- `/saves/gen-{n}-{timestamp}.json` — incremental
- `/saves/gen-{n}-final.json` — completion

Each save includes:
- Generation number
- Iteration count
- Total reward
- World state snapshot
- History length

## Phone-Only Workflow

1. Edit ROM in GitHub web editor
2. Push to repo
3. Replit auto-deploys
4. `node index.js <rom>` runs the agent

No laptop required.

---

RECEIPT: emulator-agent-core/ (4 files + README)
NEXT: Phase 2 — ROM Specification + First ROM
WHAT_NOT_TO_TOUCH: Credentials, billing, external publishing