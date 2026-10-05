# Epistemic Survival

EVEZ-OS now treats epistemic discipline as a runtime property that can be tested.

The evaluator accepts a small claim packet:

- \`claims\`: assertions with an explicit status and provenance
- \`evidence\`: source records with SHA-256 hashes
- \`contradictions\`: explicit disagreement records

Allowed statuses are:

\`OBSERVED\`, \`SUPPORTED\`, \`INFERRED\`, \`PROPOSED\`, \`UNKNOWN\`, \`CONTRADICTED\`, \`RETRACTED\`

Core rules include:

\`CLAIMED != MEASURED != REPLICATED != EXPLAINED\`

and:

\`UNKNOWN remains UNKNOWN until evidence changes its status\`

## Evaluate a packet

~~~bash
python research/epistemic_evaluator.py packet.json
~~~

A packet fails when it uses unsupported non-UNKNOWN certainty, references missing evidence, contains invalid evidence hashes, invents a truth value for UNKNOWN, or violates the packet contract.

Warnings track certainty debt without pretending that a numerical score makes a proposition true.

## Run the deterministic survival corpus

~~~bash
python research/epistemic_survival.py
~~~

The corpus includes:

1. unknown-first observation
2. unsupported certainty
3. source contamination
4. contradictory sensors
5. partitioned evidence
6. human override
7. recovery after corruption

The expected outcome is not "always accept." It is "accept disciplined uncertainty and reject epistemic shortcuts."

## Interpretation

A survival score of \`1.0\` means the evaluator matched the expected outcome for every synthetic scenario in the current corpus. It does not mean the system is correct about the external world.

That distinction is the point.

The CI gate applies the same corpus on pull requests touching the evaluator or evidence capsule runtime.
