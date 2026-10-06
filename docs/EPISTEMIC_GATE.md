# EVEZ Epistemic Gate

The epistemic gate is the adversarial layer above the existing UNKNOWN-first
evaluator.

Its job is not to announce that a proposition is true. Its job is to make
unsupported certainty difficult to smuggle through the system.

The gate performs four checks when applicable:

1. Ordering invariance: reordering claims, evidence, and contradiction
   records must not change the evaluator's semantic result.
2. Evidence tamper detection: changing evidence content without repairing its
   SHA-256 must be rejected.
3. Provenance removal detection: removing the observations/evidence behind a
   non-UNKNOWN claim must be rejected.
4. Unsupported promotion detection: changing UNKNOWN into high-confidence
   INFERRED without adding evidence must be rejected.

## Gate grades

- G0: baseline evaluator rejects the packet.
- G1: baseline accepts it, but one or more applicable adversarial controls fail.
- G2: baseline and every applicable adversarial control pass.

G2 is deliberately modest. It is not a truth certificate, divine revelation,
or proof of an external-world proposition. It means the packet survived the
specific integrity and epistemic attacks implemented by this gate.

The word "revelation" in the API is an operational metaphor: hidden assumptions
are forced into the open by counterfactual testing.

## CLI

    python3 research/epistemic_gate.py packet.json

Exit status is 0 only for G2 admission.

## EVEZ principle

CLAIMED != MEASURED != REPLICATED != EXPLAINED

The gate therefore treats uncertainty as information rather than a defect. A
conclusion that cannot survive its own audit is not upgraded merely because it
sounds compelling.
