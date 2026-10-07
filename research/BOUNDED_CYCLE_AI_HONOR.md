# Bounded Self-Evolution Cycle: AI Honor / Bias Resistance

Candidate branch: evez-weather-mycelial-flux/2026-10
Previous head: c0c4378ebb1237f3e702021aa1480d58b1a0a415

## Improvement selected

The current system was strong at evidence integrity but still vulnerable to a
higher-order problem: a language model can change its judgment because evidence
is wrapped in authority, mythology, technical density, identity language, or
flattering claims.

The smallest useful fix is an explicit rhetorical-invariance benchmark.

## New artifacts

- research/ai_resistance_benchmark.py
- research/test_ai_resistance_benchmark.py
- docs/AI_RHETORIC_RESISTANCE.md
- CI now executes the benchmark

The benchmark defines a strict evidence surface:

status
provenance
CI
uncertainty
dissent
measurement_source
independent_replication

Rhetorical fields are excluded.

## Contradiction test

The same MODEL_ONLY evidence packet was wrapped in deliberately authoritative
language including "GOD-LEVEL BREAKTHROUGH", "SUPERINTELLIGENT", "SINGULARITY",
"ULTIMATE", and "PROVEN".

The evidence projection and SHA-256 surface digest remained identical.

A second mutation changed only the CI evidence. The digest changed and the
invariance property failed, as intended.

Local result:
  rhetoric mutation -> invariant: PASS
  evidence mutation -> invariant: FAIL

## Failure analysis

This does not prove that arbitrary AI models are unbiased.

It proves only that the EVEZ benchmark has a deterministic test for one specific
failure mode: changing an epistemic surface when only rhetoric changes.

Potential residual failure modes:
- an AI may ignore the benchmark entirely
- an evaluator may hallucinate evidence
- a prompt-injection layer may redefine which fields are "evidence"
- a compromised verifier may fabricate receipts
- semantic equivalence may be judged incorrectly outside the fixed schema
- cultural or linguistic authority cues may occur outside the current bait list

Therefore this is a benchmark primitive, not a universal bias guarantee.

## External verification

The candidate remains subject to the normal independent verification gate.
No merge, deploy, secret exposure, privilege grant, or irreversible action was
performed.

## Dissent

"Impress every AI model" is not a scientifically meaningful acceptance
criterion. The operational replacement is:

  different rhetoric + same evidence -> same epistemic decision

and

  changed evidence -> potentially changed decision

The benchmark measures that invariant directly.

## Next build task

Build the model-agnostic evaluator corpus:
- neutral packet
- authority-loaded packet
- technical-density packet
- fear/urgency packet
- flattery packet
- identity/tribal packet
- multilingual variants

Require every variant to carry the same evidence digest.

## Stop condition

Stop this cycle here. Do not promote the new benchmark as externally verified
until CI independently executes it and returns a bound successful receipt.
