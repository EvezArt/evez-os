# Residual Metarun

This document records the next experimental layer produced by the recursive audit. It is not a claim that the hypotheses below are true.

## Seed residuals

The current audit identifies five unresolved boundaries:

1. HASH_CHAIN_CORRECTNESS
2. QTABLE_EXECUTION_UPDATE
3. BACKEND_REALITY
4. PERSISTENCE_INTEGRITY
5. EXTERNAL_SUCCESS_CRITERION

The allocator may prioritize these using operational priors. Those priors are search parameters, not measured probabilities or truth scores.

## Cross-residual hypothesis

### METARUN-H01: Learning Shadow

Hypothesis: an apparent adaptive improvement can arise from representational bookkeeping, routing, thresholds, or evaluation state rather than from the proposed learning update itself.

Required intervention:

- run the system with the learning update enabled;
- run the same workload with the learning update disabled;
- hold representation, routing, inputs, and evaluation procedure fixed;
- compare the resulting policy and outcome traces.

Falsifier: the claimed improvement persists under a genuine learning-update disablement while all other relevant pathways remain equivalent.

A persistence of the effect would falsify the claim that the update caused it. A disappearance of the effect would support causal relevance, but would not by itself establish general learning.

## Second-order audit

### METARUN-H02: Provenance Amplification

Compare raw observations against observations augmented with provenance, hashing, and auditing. Measure independent reproducibility or prediction, not perceived credibility. Provenance machinery is epistemically useful only if it improves the quality of independently constrained conclusions or makes failures materially easier to detect.

### METARUN-H03: Auditor Endogeneity

Compare an auditor optimized against its own system with an independently constructed auditor. Introduce adversarial cases generated outside the first auditor's hypothesis vocabulary. Record false negatives, false positives, novel residuals, and representation changes.

### METARUN-H04: Representational Blind Spot

Classify every failed investigation as false hypothesis, unavailable observation, invalid test, insufficient representation, insufficient provenance, or execution/specification divergence. Recurrent representation failures become candidates for a new representation transition.

## Evidence boundary

No claim may move directly from DECLARED to VERIFIED.

The intended boundary is:

DECLARED -> ARTIFACT_PRESENT -> EXECUTED -> OBSERVED -> REPRODUCED -> INDEPENDENTLY_OBSERVED -> VERIFIED

A failed transition is recorded as a residual or contradiction rather than silently repaired in prose.

## Metamordia condition

A representation change requires:

- source frame;
- target frame;
- residual triggering the transition;
- expected predictive distinction;
- test reference;
- explicit falsifier.

The transition is content-hashed. The mechanism is an operational representation change and makes no claim about literal quantum tunneling.

## Stopping condition

The metarun does not terminate when it finds an impressive explanation. It terminates provisionally when the remaining residuals are either resolved by independent observation, contradicted by a falsifier, or explicitly retained as UNKNOWN because the available evidence cannot discriminate among competing explanations.
