# EVEZ Evidence Runtime

Executable epistemic/adversarial runtime for bounded synthetic testing.

Core pipeline:

`CLAIM → TERMS → OBSERVABLES → TEST → ACTION → OBSERVATION → INVARIANTS → ROLLBACK → RECEIPT`

The runtime separates operational rollback from historical evidence. A failed test is not deleted by rollback. A passing test is not treated as proof of the broader claim.

## Safety boundary

The included mutations operate on an in-memory synthetic target. The package does not execute arbitrary shell commands, contact external services, obtain credentials, or attempt real-world exploitation.

## Run

```bash
PYTHONPATH=src python -m evez_evidence_runtime.cli self-audit
```

## Test

```bash
PYTHONPATH=src pytest -q
```

## Epistemic rule

`CLAIMED ≠ MEASURED ≠ REPLICATED ≠ EXPLAINED`

A receipt establishes that this runtime executed a bounded test and recorded its result. It does not establish universal truth of the broader claim.
