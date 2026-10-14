# EVEZ Evidence Runtime

Executable epistemic/adversarial runtime for bounded synthetic testing.

Core pipeline:

`CLAIM → TERMS → OBSERVABLES → TEST → ACTION → OBSERVATION → INVARIANTS → ROLLBACK → RECEIPT`

Optimization pipeline:

`CANDIDATES → SAFETY GATE → OBSERVABILITY GATE → DISCRIMINATION GATE → DOMINANCE PRUNING → VALUE/COST RANKING → BOTTLENECK UPDATE`

The runtime separates operational rollback from historical evidence. A failed test is not deleted by rollback. A passing test is not treated as proof of the broader claim.

## Maximum-optimization layer

The optimizer does not collapse epistemic state into a confidence score. It selects bounded experiments using hard gates and deterministic ordering:

1. reject unsafe tests;
2. reject tests without observables;
3. reject non-discriminating tests;
4. reject tests that cannot affect the claim;
5. reject tests outside the risk budget;
6. remove strictly dominated experiments;
7. prioritize contradiction resolution;
8. prioritize information gained per cost;
9. preserve reproducibility and low risk as tie-breakers.

The optimizer also exposes dependency bottlenecks. A downstream claim depending on an UNKNOWN ancestor remains epistemically constrained until new evidence changes that dependency.

The package includes claim lineage, explicit falsifiers, and an epistemic-conservation guard. The guard prevents UNKNOWN/PROPOSED state from becoming VERIFIED merely because a later component writes a more confident sentence.

## Safety boundary

The included mutations operate on an in-memory synthetic target. The package does not execute arbitrary shell commands, contact external services, obtain credentials, or attempt real-world exploitation.

## Run

```bash
PYTHONPATH=src python -m evez_evidence_runtime.cli self-audit
PYTHONPATH=src python -m evez_evidence_runtime.cli optimize
```

## Test

```bash
PYTHONPATH=src pytest -q
```

## Epistemic rules

`DECLARED != EFFECTIVE`

`CLAIMED != MEASURED != REPLICATED != EXPLAINED`

`PROVENANCE != TRUTH`

A receipt establishes that this runtime executed a bounded test and recorded its result. It does not establish universal truth of the broader claim.

An optimization result establishes only a selected experiment under the current candidate set, constraints, budget, and evaluator. It does not establish a global optimum.

A VERIFIED promotion requires preserved observations, tests, falsifiers, no unresolved contradiction in the lineage, and new evidence. Otherwise the promotion is blocked.

## Recovery optimization

Recovery is a separate optimization problem from experiment selection. The recovery engine classifies a failure, generates admissible alternatives, applies safety/authority/observability/budget gates, removes dominated actions, and selects a bounded candidate without executing it.

Supported recovery states include `OBSERVED_FAILURE → CLASSIFIED → ALTERNATIVES_GENERATED → ALTERNATIVES_FILTERED → RECOVERY_SELECTED → EXECUTING → VERIFIED_RECOVERY / NEXT_ALTERNATIVE / CAIN / EVIDENCE_PENDING / QUARANTINED`.

Hard recovery rules include:

- unsafe actions are rejected;
- unauthorized actions are rejected;
- non-observable actions are rejected;
- retries require idempotency or explicit compensation;
- risk and blast radius are budgeted;
- dominated alternatives are pruned;
- integrity failures route toward CAIN/quarantine rather than fabricated recovery;
- a recovery decision is not evidence that recovery occurred.

Run the synthetic recovery planner with:

```bash
PYTHONPATH=src python -m evez_evidence_runtime.cli recover
```


## Unified operational planner

The runtime now has a planner that arbitrates between evidence collection and recovery instead of treating every failure as a retry problem:

`CLAIM STATE + FAILURE CLASS + CANDIDATES → NEXT ACTION`

Possible outputs are:

- `TEST`: gather discriminating evidence;
- `RECOVER`: select a bounded recovery alternative;
- `QUARANTINE`: preserve a contradiction or unsafe authority boundary;
- `HUMAN_REVIEW`: require explicit authority adjudication;
- `EVIDENCE_PENDING`: refuse to manufacture an answer;
- `NO_ACTION`: no bounded action is required.

The planner applies contradiction and authorization gates before ordinary recovery selection. A system therefore cannot use "recovery" as a backdoor for authority escalation.

