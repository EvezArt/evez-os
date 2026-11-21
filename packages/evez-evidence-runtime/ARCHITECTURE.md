# EVEZ Evidence Runtime Architecture

WORLD -> OBSERVATIONS -> WITNESSES -> CLAIMS -> TESTS -> CONTRADICTIONS -> MODELS -> EXPLANATIONS -> ACTIONS -> WORLD

The package is intentionally smaller than the full architecture. Each component has an explicit contract.

## Components

- SurfaceMapper: declares trust, authority, data, execution, and observation boundaries.
- ThreatEngine: converts a surface into bounded synthetic test cases.
- MutationRegistry: permits only registered mutations with explicit safety bounds.
- Observer: records before/action/after state and canonical hashes.
- InvariantBattery: evaluates typed predicates and preserves failures.
- RollbackController: restores operational state without erasing witness history.
- ClaimCompiler: translates claims into terms, observables, and evidence requirements.
- EvidenceSpine: append-only SHA-256 event chain.
- WitnessEnvelope: normalizes external provider observations without granting automatic truth.
- EvidenceBridge: compares provider witnesses while preserving disagreement.
- DependencyGraph: exposes epistemic debt and dependency blast radius.
- CounterfactualEngine: compares observations against competing hypotheses.
- SelfAuditor: checks that the apparatus has a valid witness history.

## Runtime contract

1. Snapshot state.
2. Map the failure surface.
3. Select one bounded mutation.
4. Record pre-state.
5. Execute against the synthetic target.
6. Record post-state.
7. Evaluate invariants.
8. Calculate delta.
9. Restore operational state.
10. Verify restoration.
11. Emit an immutable receipt.
12. Classify PASS, VIOLATION, CONTRADICTION, or UNKNOWN.

## Epistemic invariants

DECLARED != EFFECTIVE

CLAIMED != MEASURED != REPLICATED != EXPLAINED

PROVENANCE != TRUTH

A receipt establishes that a bounded test ran and what it observed. The receipt is not universal proof.

## Cross-provider junction

A future read-only integration can form:

GitHub commit -> Vercel deployment -> Supabase state -> runtime observation -> Asana operational claim -> EVEZ witness receipt

Each node remains a witness. A mismatch becomes a contradiction record rather than being silently reconciled.

## Scope

The first implementation is local and synthetic. External provider adapters should remain read-only until separately authorized and tested.
