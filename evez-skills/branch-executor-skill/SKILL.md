# EVEZ Branch Executor Skill

Parallel branch execution engine for AI agents. Run multiple code branches, test variations, and merge the best result automatically.

## What It Does

- **Parallel Execution**: Run multiple code branches simultaneously
- **Branch Testing**: Test variations against the same input
- **Auto-Merge**: Automatically select and merge the best performing branch
- **Receipt Logging**: Every execution logged with results

## Installation

```bash
pip install -r requirements.txt
```

(No external deps - uses stdlib)

## Usage

```python
from branch_executor import BranchExecutor

executor = BranchExecutor()

# Add branches
executor.add_branch("branch_a", lambda x: x * 2)
executor.add_branch("branch_b", lambda x: x + 10)

# Run parallel
results = executor.run_parallel(5)

# Get best
best = executor.get_best()
```

## CLI

```bash
python3 branch_executor.py --test
python3 branch_executor.py --run branch_a,branch_b --input 42
```

## Use Cases

- A/B testing at code level
- Algorithm optimization
- Parallel hypothesis testing

## Micro-license: $9-19 per skill. Do not redistribute. See LICENSE.

MIT