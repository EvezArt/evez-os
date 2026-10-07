# Semantic Intent and Rights Runtime

The runtime now treats words as structured inputs rather than opaque prompt
strings.

## Semantic mapping

research/lexile_semantics.py produces:

- token and n-gram atoms
- abstraction density
- syllable estimate
- information proxy bits
- semantic role classification
- coined-term recognition
- deterministic content-complexity proxy

The output is explicitly:

    INTERNAL_PROXY_NOT_CERTIFIED_LEXILE

It is not a certified Lexile measure.

User-defined or newly coined expressions can be entered into the same semantic
space without pretending that they are established external terms.

## Intent precision

research/precision_contract.py rejects vague executable intent until a
specification exists for:

    subject
    action
    scope
    inputs
    constraints
    evidence
    acceptance
    time
    authority

## Rights and licensing

legal/license_opportunity.py audits files for declared licenses and maps them
to candidate commercial pathways.

It never treats a missing license as permission.

The ownership-first state machine is:

    UNDECLARED -> REVIEW
    DECLARED -> CANDIDATE
    THIRD_PARTY -> PRESERVE
    OWNERSHIP_UNKNOWN -> DO_NOT_GRANT

## Runtime objective

The combined system seeks:

    highest verified user-value
    --------------------------------
    ambiguity + compute + latency + risk + human attention

subject to evidence and authority constraints.

"Fix everything" therefore becomes a measurable optimization problem rather than
an unlimited promise.
