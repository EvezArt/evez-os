# EVEZ Ledger Skill - RUNBOOK

## Quick Start

```bash
# Copy to project
cp -r evez-ledger-skill/ /your/project/

# Initialize ledger
cd evez-ledger-skill
python3 ledger.py --init
```

## Observable Metrics

### Track Chain Reaction

```bash
# Count entries
wc -l chain.jsonl

# Verify integrity
python3 ledger.py --verify

# Check recent entries
tail -5 chain.jsonl
```

## Integration

The Ledger integrates with:
- Revenue Engine: log each revenue action
- Self Compiler: log validation results
- OctoKlaw: use as source of truth

## CLI Reference

| Command | Description |
|---------|-------------|
| `--init` | Create genesis block |
| `--append <json>` | Add entry to chain |
| `--verify` | Check chain integrity |
| `--status` | Show ledger stats |
| `--tail [n]` | Show last n entries |

## Architecture

```
ledger/
├── spine.jsonl   # Quick index
└── chain.jsonl  # Full chain (hash-chained)
```