# Recursive Measurement Protocol

This repository now contains an evidence-bound audit layer for tracing the gap between intended behavior and observed behavior.

## Generation record

Each generation records:

1. intention
2. artifact
3. execution
4. observation
5. source references
6. reproducible transformation references
7. typed discrepancies
8. residuals / candidate variables
9. model revision
10. parent generation hash

The record is hash-linked so a later generation cannot silently replace an earlier observation.

## Evidence rule

`UNKNOWN` is the default when an observation or source is missing. A reproducible transformation can elevate an observed, sourced result to `VERIFIED`, but it never erases prior contradictions.

The intended and behavior-inferred models are kept separately. `compare_models()` returns per-dimension divergence rather than a fabricated scalar score.

## Causal categories

Discrepancies are classified as intention/artifact, artifact/execution, execution/observation, measurement/interpretation, temporal, provenance, causal, observer-effect, self-model, or unknown.

## Audit the auditor

A recursive audit is incomplete if the auditor itself can rewrite its latest record without detection. `RecursiveAuditor.seal()` creates an externalizable commitment containing generation count, head hash, and a manifest hash over the complete generation and model-divergence state. `verify_seal()` detects mutation, and a sealed auditor rejects further appends. The seal is a commitment, not a signature or proof of truth. It must be stored outside the mutable auditor state to provide meaningful independent anchoring.

## Current EVEZ-OS residuals identified during the initial audit

- `PERSISTENCE_INTEGRITY`: the inspected EventSpine stores events in process memory; durable restart survival is not established.
- `HASH_CHAIN_CORRECTNESS`: the inspected implementation assigns the newly computed hash to `hash_prev`, so the field does not contain the preceding hash as its name suggests.
- `EXTERNAL_SUCCESS_CRITERION`: patch learning is driven by the local `QuantumResult.success` and backend fields; independent task correctness is not established.
- `QTABLE_EXECUTION_UPDATE`: the contextual bandit exposes a Q-table update method, while the inspected anomaly-analysis path selects an action without visibly updating that Q-table.
- `BACKEND_REALITY`: the inspected RQNS path constructs a mocked solver result; external quantum execution is not established by that path.

These are investigation records, not claims about intent or motive.
