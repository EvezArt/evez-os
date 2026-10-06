# Observer Externality Guard

The Observer Externality Guard isolates the feedback path:

O → I → P → M → R → O'

O is the observation existing before the interaction.
I is interpretation.
P is the prompt constructed from available state.
M is model output.
R is observer reaction.
O' is the subsequent observation.

The constitutional rule is:

> Internally generated representations cannot increase the evidentiary status of a claim.

This is an evidence-boundary rule. It does not make claims about intelligence, consciousness, deception, or intent. It controls provenance.

## Invariants

MODEL_OUTPUT_CANNOT_VALIDATE_ITS_OWN_PREMISES

A model response may transform or summarize existing evidence. The response itself is not independent corroboration.

representation_count != evidence_count

Writing the same proposition ten different ways creates ten representations, not ten independent observations.

internal_evidence_weight = 0

Model output, prompts, interpretations, observer reactions, and synthetic or derived records contribute zero independent evidentiary weight.

## Promotion gate

A claim may pass the externality gate only when at least one observation is explicitly marked external and has traceable provenance.

Externality does not mean truth. The gate only establishes that the source is outside the model/observer feedback loop. Source quality, authenticity, relevance, and contradiction remain separate tests.

Unknown provenance is never silently promoted to external provenance.

## Failure codes

- INTERNAL_ORIGIN
- MODEL_DERIVED_OBSERVATION
- SELF_CONFIRMATION
- UNKNOWN_PROVENANCE
- EXTERNAL_STATE_TRANSITION

The last code is informational. It means the trace contains an explicitly external subsequent state transition that can be considered by the wider Claim-to-Reality pipeline.

The guard deliberately does not return VERIFIED. A provenance gate is not a truth oracle.
