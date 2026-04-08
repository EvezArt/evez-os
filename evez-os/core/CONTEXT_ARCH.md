# EVEZ CONTEXT ARCHITECTURE

## The Problem
Context is scattered across:
- Session memory (chat history)
- Daily notes (memory/YYYY-MM-DD.md)
- Long-term (MEMORY.md)
- Ledger (ledger/spine.jsonl, chain.jsonl)
- Trunk state (trunk/state.json)
- Kai state (.kai_state.json)

**They don't talk to each other.**

---

## The Solution: Two-Layer Context System

### LAYER 1: SHORT-TERM CONTEXT (STM)
| Source | TTL | Purpose |
|--------|-----|---------|
| Active session | Current turn | What I'm working on right now |
| .kai_state.json | Session | Current task progress, pending actions |
| Daily notes | 24h | Today's events, decisions made |
| Trunk state | Until objective complete | Current objective, branches |

**Access pattern:** Fast, in-memory, session-scoped

### LAYER 2: LONG-TERM CONTEXT (LTM)
| Source | TTL | Purpose |
|--------|-----|---------|
| MEMORY.md | Forever | Who Steven is, preferences, lessons learned |
| ledger/*.jsonl | Forever | All decisions, events, state changes |
| AGENTS.md | Forever | How I work, skills, constraints |

**Access pattern:** Semantic search, file lookup, cross-session

---

## CROSS-LAYER FLOW

```
SHORT-TERM                          LONG-TERM
    │                                   │
    ▼                                   ▼
┌─────────┐                       ┌─────────┐
│ Current │ ◄──► CONTEXT BRIDGE ◄─►│ MEMORY  │
│ Session │                       │  Ledger │
└─────────┘                       └─────────┘
    │                                   │
    └───────────► SYNC ◄───────────────┘
                    │
         ┌────────┴────────┐
         │                 │
      DECISION          LEARNING
      (commit)         (extract)
```

---

## CONTEXT BRIDGE RULES

### On Every Decision:
1. **READ**: Check LTM for relevant history
2. **DECIDE**: Make choice in STM
3. **COMMIT**: Write to both layers

### On Session End:
1. **EXTRACT** from STM → daily notes
2. **SUMMARIZE** → MEMORY.md if significant
3. **APPEND** → ledger (immutable record)

### On Session Start:
1. **LOAD** MEMORY.md (long-term)
2. **LOAD** today's notes (short-term)
3. **RECONCILE** → current trunk objective

---

## FILE STRUCTURE

```
evez-os/core/
├── context/
│   ├── stm.json          # Short-term context (current session)
│   ├── ltm_index.json    # Long-term reference map
│   └── bridge.py         # Context bridge logic
├── ledger/
│   ├── spine.jsonl       # Immutable event log
│   └── chain.jsonl       # Decision chain
└── trunk/
    └── state.json        # Current objective + branches
```

---

## IMPLEMENTATION PRIORITY

### PHASE 1: Bridge (Today)
- [ ] Create context/bridge.py
- [ ] Add sync_to_ltm() function
- [ ] Add load_context() function

### PHASE 2: Integration (This Week)
- [ ] Hook into autonomous_runner
- [ ] Every cycle reads LTM before deciding
- [ ] Every cycle writes to both layers

### PHASE 3: Intelligence (This Month)
- [ ] Semantic search across ledger
- [ ] Pattern detection (what works, what doesn't)
- [ ] Auto-extract lessons to MEMORY.md

---

## USAGE

```python
from context.bridge import ContextBridge

ctx = ContextBridge()

# On decision made:
ctx.commit_decision(
    decision="Started EVEZ daemon",
    rationale="Need autonomous execution",
    outcome="Daemon running, 60s interval"
)

# On session start:
context = ctx.load_full_context()
# Returns: {stm, ltm_summary, trunk_state, recent_decisions}
```
