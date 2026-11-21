# EVEZ Canonical Corpus Ontology v0.1.0

The corpus is modeled as a typed evidence graph plus an append-only evidence-event layer.

## Core invariant

```
NARRATIVE
   ↓
CLAIM
   ↓
TERMS / OBSERVABLES / SOURCES / ASSUMPTIONS
   ↓
TRANSFORMS
   ↓
TESTS
   ↓
RESULT
   ↓
SUPPORT / CONTRADICTION
   ↓
STATE
   ↓
DECISION
```

`CLAIMED ≠ MEASURED ≠ REPLICATED ≠ EXPLAINED`

`PROVENANCE ≠ TRUTH`

`DECLARED ≠ EFFECTIVE`

## Node types

PERSON, PROJECT, REPOSITORY, DOCUMENT, CODE, MODEL, DATASET, EVENT, CLAIM, OBSERVATION, MEASUREMENT, ASSUMPTION, SOURCE, TRANSFORMATION, TEST, RESULT, CONTRADICTION, DECISION, STATE, RUN, REVIEW, POLICY.

## Edge types

ASSERTS, ABOUT, DERIVED_FROM, OBSERVED_BY, MEASURES, SUPPORTS, CONTRADICTS, TESTS, PRODUCES, USES, REPRODUCES, REFERENCES, SUPERSEDES, RETRACTS, GOVERNS, TRIGGERS, AFFECTS, DECIDES, PARENT_OF.

## Claim state

UNKNOWN → PROPOSED → INFERRED → SUPPORTED → VERIFIED

Orthogonal evidence dimensions:

- measurement: NOT_MEASURED | MEASURED | REMEASURED
- reproduction: NOT_TESTED | ATTEMPTED | REPRODUCED | FAILED_TO_REPRODUCE
- explanation: UNEXPLAINED | PARTIALLY_EXPLAINED | EXPLAINED

Terminal/side states:

- CONTRADICTED
- STALE
- RETRACTED

A result can be reproduced without the proposition being true. A provenance link can be complete without the proposition being true. The model therefore keeps evidence dimensions separate.

## Evidence event

Each significant execution may carry:

```json
{
  "event_id": "evt-...",
  "event_type": "TEST_RESULT",
  "timestamp": "ISO-8601",
  "source": "...",
  "code_commit": "...",
  "environment": "...",
  "inputs_hash": "...",
  "parameters_hash": "...",
  "output_hash": "...",
  "operator": "...",
  "parent_event_hash": "...",
  "payload": {}
}
```

Historical correction is represented by a new event. The old event is not edited in place.

## Graph semantics

```
SOURCE ──ASSERTS──────> CLAIM
OBSERVATION ──SUPPORTS→ CLAIM
OBSERVATION ──CONTRADICTS→ CLAIM
TEST ──TESTS─────────> CLAIM
RUN ──USES───────────> ARTIFACT
RUN ──PRODUCES───────> RESULT
RUN ──REPRODUCES─────> RESULT
DECISION ──DECIDES────> CLAIM / RESULT / RISK
POLICY ──GOVERNS─────> OPERATION / SYSTEM
```

The semantic graph explains relationships. The evidence spine records what actually happened in the evidence system.

## Corpus ingestion rule

A source statement enters the corpus first as an assertion by that source. Ingestion must not silently upgrade authorship into verification.

The canonical runtime should be able to answer:

1. What was asserted?
2. By whom or what source?
3. What was directly observed?
4. What was measured?
5. Which transformations were performed?
6. Which tests were actually run?
7. What contradicted the claim?
8. What has been independently reproduced?
9. What remains unknown?
10. Which decision depends on the result?
