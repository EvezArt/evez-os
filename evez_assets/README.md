# EVEZ Assets - Autonomous System Components

EVEZ-style modules for building autonomous agent systems with self-improvement loops. All stdlib-compatible (no numpy/pandas dependencies).

## Components

| Module | Purpose | CLI |
|--------|---------|-----|
| `spine.py` | Append-only event log with cryptographic chain | `launcher.py spine` |
| `autonomous_agent.py` | RL agent with hot-swapping thresholds | `launcher.py agent` |
| `memory_store.py` | Unified memory with semantic search + decay | `launcher.py memory` |
| `cognition_engine.py` | FIRE events (F/I/R/E) with topology | `launcher.py cognition` |
| `autonomous_loop.py` | OODA self-improvement cycle | `launcher.py loop` |
| `swarm_orchestrator.py` | Multi-agent coordination | `launcher.py swarm` |
| `finance_engine.py` | Trading, income loops, portfolio | `launcher.py finance` |
| `api_server.py` | HTTP API for all modules (port 8765) | `python3 api_server.py` |
| `launcher.py` | Unified entry point | `launcher.py [command]` |

## Quick Start

```bash
cd /root/.openclaw/workspace/evez_assets

# Run individual modules
python3 launcher.py spine
python3 launcher.py agent
python3 launcher.py memory
python3 launcher.py cognition
python3 launcher.py loop
python3 launcher.py swarm
python3 launcher.py finance

# Run full integrated system
python3 launcher.py full

# Start HTTP API
python3 api_server.py
```

## Usage

```python
from spine import EventSpine
from autonomous_agent import ContextualBanditAgent
from memory_store import UnifiedMemory
from cognition_engine import CognitionEngine
from autonomous_loop import AutonomousLoop
from swarm_orchestrator import SwarmOrchestrator, TaskPriority
from finance_engine import FinanceEngine
```

## API Server

Start with: `python3 api_server.py`

Endpoints:
- `GET /health` - System health
- `GET /spine` - Event spine state
- `GET /agent` - Agent stats
- `GET /memory` - Memory stats
- `GET /cognition` - Cognition topology
- `GET /loop` - Loop status
- `GET /swarm` - Swarm status
- `GET /finance` - Finance performance
- `GET /full` - Full system cycle
- `POST /agent/decide` - Make decision
- `POST /memory/store` - Store memory
- `POST /memory/search` - Search memory
- `POST /cognition/fire` - Create FIRE event
- `POST /swarm/register` - Register agent
- `POST /swarm/task` - Submit task
- `POST /finance/order` - Place order

## Architecture

```
┌─────────────────────────────────────────────┐
│           Autonomous Loop                    │
│   (Observe → Orient → Decide → Act)          │
└────────────────┬────────────────────────────┘
                 │
    ┌────────────┼────────────┬─────────────┐
    ▼            ▼            ▼             ▼
┌───────┐   ┌───────┐   ┌─────────┐   ┌─────────┐
│Spine  │   │Memory │   │Cognition│   │ Finance │
│(Log)  │   │(Store)│   │(FIRE)   │   │(Trading)│
└───────┘   └───────┘   └─────────┘   └─────────┘
                 │            │
                 ▼            ▼
          ┌──────────────┐ ┌──────────────┐
          │Agent (Decide)│ │Swarm (Coord) │
          └──────────────┘ └──────────────┘
```

## Integration with OpenClaw

These modules can be called via exec tool or as an OpenClaw skill (see SKILL.md).

## License

MIT - EVEZ-style open autonomous systems