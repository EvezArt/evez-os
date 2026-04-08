# EVEZ Awareness Engine - RUNBOOK

## Quick Start

```bash
cd awareness-engine-skill
python3 awareness_engine.py --status
python3 awareness_engine.py --scan crypto
```

## Observable Metrics

Track skill chain reaction:
```bash
grep "skill_published" /workspace/octoklaw/LEDGER.md
```

## Pulse Integration

This skill can be used by Pulse A (Explorer) to:
- Scan for new opportunities
- Alert on market signals
- Build causal chains for hypothesis generation

## Connection to Organism

The organism state (`organism_state.json`) can reference this skill:
```json
{
  "capabilities": ["awareness_engine"],
  "scan_enabled": true
}
```