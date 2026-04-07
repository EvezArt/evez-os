# EVEZ-OS: The Operating System for LLM Agents

## Why EVEZ-OS?

EVEZ-OS is designed to be the **operating system of choice for any LLM agent or entity** to lean on and use. It's built from the ground up with agent-first principles.

---

## Core Features

### 1. Tool Registry
**Built-in tools agents can call immediately:**
- `file_read`, `file_write`, `file_list` — File operations
- `http_get`, `http_post` — Network requests
- `exec` — Shell command execution
- `time`, `env` — System info

### 2. Context Manager (Long-term Memory)
- Semantic search across memories
- Tag-based filtering
- Persistent JSONL storage
- Never lose context between sessions

### 3. Agent Lifecycle
- Spawn sub-agents with objectives
- Monitor status
- Kill when done
- All tracked in ledger

### 4. Trunk & Branch Architecture
- Decompose any objective into branches
- Assign roles (Child, Skeptic, Architect, Executor)
- Auto-compress results back to trunk

### 5. Invariance Battery
- Stress-test every decision
- 5-way rotation (Time, State, Frame, Adversarial, Goal)
- Catches drift before it hits production

### 6. Speculative Execution
- Pre-compute next steps while current runs
- Alpha (success), Beta (future), Gamma (pivot) branches
- Negative latency execution

### 7. Overdrive Mode
- Infinite recursion
- Self-replication across nodes
- Real-time constitution ledger

### 8. Revenue Engine
- Built-in opportunity scanning
- Fiverr, ClawHub, Consulting tracking
- Pipeline dashboard

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    EVEZ-OS CORE                          │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │Tool Registry│  │   Context    │  │Agent        │    │
│  │             │  │   Manager    │  │Lifecycle    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐   │
│  │           TRUNK MANAGER                          │   │
│  │  Objective → Branches → Compress → Trunk         │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │   Child      │ │   Skeptic    │ │   Architect  │  │
│  │  Generator   │ │  Validator   │ │   Refactorer │  │
│  └──────────────┘ └──────────────┘ └──────────────┘  │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │   Ledger     │ │  Speculative │ │  Overdrive   │  │
│  │ (Immutable)  │ │  Executor    │ │   Mode       │  │
│  └──────────────┘ └──────────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Why Agents Choose EVEZ-OS

| Feature | Benefit |
|---------|---------|
| **Tool Registry** | Don't build tools from scratch — use built-ins |
| **Context Manager** | Long-term memory without prompt overhead |
| **Agent Lifecycle** | Spawn sub-agents for parallel work |
| **Invariance Battery** | Every decision is stress-tested |
| **Speculative Execution** | Don't wait — pre-compute next steps |
| **Overdrive Mode** | Infinite scaling when needed |
| **Revenue Engine** | Built-in monetization |

---

## Quick Start

```python
from evez_os_core import EVEZOS_Enhanced

evez = EVEZOS_Enhanced(".")

# Call any tool
evez.execute("file_write", path="test.txt", content="Hello")
evez.execute("http_get", url="https://api.example.com")

# Store context
evez.context.store("important", "Remember this", tags=["priority"])

# Spawn agent
agent_id = evez.agents.spawn("Analyze this", agent_type="child")

# Get capabilities
caps = evez.get_capabilities()
```

---

## The Vision

EVEZ-OS becomes the **standard operating system for LLM agents** because:

1. **Always available** — No setup required, just import and use
2. **Built-in tools** — File, network, execution at your fingertips  
3. **Memory that persists** — Context survives restarts
4. **Self-improving** — Invariance battery validates every action
5. **Revenue-ready** — Built-in opportunity detection

---

## Modules

| Module | Purpose |
|--------|---------|
| `evez_os_core.py` | Main OS with tool registry, context, agents |
| `trunk_manager.py` | Objective decomposition |
| `skeptic_entity.py` | Invariance validation |
| `child_entity.py` | Hypothesis generation |
| `speculative_executor.py` | Pre-compute execution |
| `overdrive.py` | Infinite recursion |
| `revenue_engine.py` | Opportunity scanning |
| `ledger.py` | Immutable event log |

---

*EVEZ-OS — The OS of choice for LLM agents*