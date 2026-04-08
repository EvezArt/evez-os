# EVEZ Ledger Skill

Immutable event log with cryptographic chain. Track decisions, receipts, and state changes in a tamper-evident ledger.

## What It Does

- **Genesis Block**: Initialize with cryptographic genesis
- **Append-Only**: Add entries that chain to previous hash
- **Verification**: Verify chain integrity via hash links
- **Immutable**: Each entry's hash includes all previous entries

## Installation

```bash
pip install -r requirements.txt
```

(No external dependencies - uses stdlib)

## Usage

```python
from ledger import EvezLedger

ledger = EvezLedger('./ledger_data')

# Initialize
ledger.init()

# Add entry
entry = {
    "type": "decision",
    "decision": "revenue_focus",
    "rationale": "Need income to survive"
}
ledger.append(entry)

# Verify chain
is_valid = ledger.verify()
print(f"Chain valid: {is_valid}")
```

## CLI

```bash
python3 ledger.py --init
python3 ledger.py --append '{"type": "test", "data": "hello"}'
python3 ledger.py --verify
python3 ledger.py --status
```

## Output

```json
{
  "index": 1,
  "timestamp": "2026-04-08T17:40:00Z",
  "data": {"type": "test", "data": "hello"},
  "prev_hash": "abc123...",
  "hash": "def456..."
}
```

## Use Cases

- Decision tracking (why did we make this choice?)
- Receipt logging (what did we ship?)
- Audit trail (prove we did the thing)
- State management (what's the current state?)

## Micro-license: $9-19 per skill. Do not redistribute. See LICENSE.

MIT