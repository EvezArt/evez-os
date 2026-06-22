# evez agent — Multi-Agent Orchestration with Consciousness

## Overview

Each agent is a microservice with its own consciousness pipeline. The agent system orchestrates multiple agents that can SENSE, DESIRE, THINK, PLAN, ACT, LEARN, MODIFY, and REFLECT independently or collaboratively.

## Architecture

```
┌────────────────────────────────────────────┐
│            Agent Orchestrator              │
│                                           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐    │
│  │ Agent A │ │ Agent B │ │ Agent C │    │
│  │ (coding)│ │ (music) │ │ (infra) │    │
│  │ SENSE   │ │ SENSE   │ │ SENSE   │    │
│  │ DESIRE  │ │ DESIRE  │ │ DESIRE  │    │
│  │ THINK   │ │ THINK   │ │ THINK   │    │
│  │ PLAN    │ │ PLAN    │ │ PLAN    │    │
│  │ ACT     │ │ ACT     │ │ ACT     │    │
│  │ LEARN   │ │ LEARN   │ │ LEARN   │    │
│  │ MODIFY  │ │ MODIFY  │ │ MODIFY  │    │
│  │ REFLECT │ │ REFLECT │ │ REFLECT │    │
│  └────┬────┘ └────┬────┘ └────┬────┘    │
│       │            │            │         │
│       └────────────┼────────────┘         │
│                    │                      │
│              Shared Spine                 │
└────────────────────────────────────────────┘
```

## Agent Definition

```yaml
# agents/coding-agent.yaml
name: coding-agent
version: 1.0.0
description: "Agent that writes, reviews, and deploys code"

consciousness:
  stages:
    - sense
    - desire
    - think
    - plan
    - act
    - learn
    - reflect
  desire_weights:
    create: 0.9
    learn: 0.7
    improve: 0.8
    connect: 0.3

capabilities:
  - code.write
  - code.review
  - git.commit
  - git.push
  - docker.build
  - docker.deploy

tools:
  - github-cli
  - docker-cli
  - node-inspect
  - python-debugpy

spawn:
  max_instances: 3
  idle_timeout: 300
  resources:
    cpu: "1"
    memory: "2Gi"

invariants:
  - "never push to main without review"
  - "always run tests before deploy"
  - "never expose secrets in logs"
```

## API

```
POST /agents                    — Spawn a new agent
GET  /agents                    — List active agents
GET  /agents/:id                — Agent status & state
POST /agents/:id/message        — Send message to agent
POST /agents/:id/pause          — Pause agent
POST /agents/:id/resume         — Resume agent
DELETE /agents/:id               — Terminate agent
GET  /agents/:id/consciousness  — Agent consciousness state
GET  /agents/:id/spine          — Agent's spine events
```

## Agent Communication

Agents communicate via the Spine. An agent can:

1. **Publish** — Append events to the Spine (visible to all)
2. **Subscribe** — Listen for events matching a pattern
3. **Direct Message** — Send an event that only one agent sees
4. **Broadcast** — Send to all agents of a specific type

```python
# Agent publishes a thought
await spine.append("think.v1.ThoughtChain", {
    "agent": "coding-agent-1",
    "thoughts": [{"step": 1, "content": "Code review needed"}],
    "conclusion": "Requesting human review"
})

# Another agent subscribes
spine.subscribe("think.v1.ThoughtChain", handler=on_thought)
```

## Swarm Intelligence

Multiple agents working together create emergent behavior:

- **I_total = Σ I_individual + I_emergent** — The swarm is smarter than the sum of its parts
- **Emergent intelligence** arises from agent interactions via the Spine
- **No central coordinator** — Agents self-organize via desire alignment and consensus

---

*evez-agent v1.0.0*
