# Kai Digital Twin

**Version:** 0.1  
**Created:** 2026-04-07  
**Parent:** Kai (main session)

---

## What This Is

A self-replicating agent that uses the **same interface** as Kai (the main session):
- Same tool access (exec, write, read)
- Same spine logging
- Same chat control surface
- Can continue without human

---

## Quick Start

```bash
# Initialize
python3 kai_twin.py init

# Run a cycle
python3 kai_twin.py run "your prompt here"

# Check status
python3 kai_twin.py status

# Execute action
python3 kai_twin.py action exec '{"command": "ls -la"}'
```

---

## Capabilities

| Action | Description | Risk |
|--------|-------------|------|
| exec | Run shell commands | medium |
| write | Write files | low |
| read | Read files | none |
| think | Process internally | none |
| spawn | Spawn sub-agents | medium |
| log | Log to spine | none |

---

## Control

Control the twin through chat:
- Message starts with `#` = think
- Contains `write FILENAME:` = write action
- Otherwise = think mode

---

## State

All twin state tracked in `.kai_twin_state.json`:
- Cycles completed
- Last action
- Memory (last 10)

---

## Integration

To make this the **one stop chat surface for all chat surfaces**:
1. Twin receives commands via chat
2. Twin executes using same tools as Kai
3. Twin logs everything to spine
4. Twin can spawn other twins for parallel work

**This IS the digital twin.**