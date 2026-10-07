# EVEZ Precision Contract

Vague language is not execution.

Before an intent can become an executable outcome, the system must be able
to identify:

    subject
    action
    scope
    inputs
    constraints
    evidence
    acceptance
    time
    authority

The precision layer flags terms that hide unbounded interpretation, including
"everything", "fully", "better", "best", "soon", "appropriate", "safe",
"secure", "complete", "perfect", and similar expressions.

This is intentionally conservative.

A flagged term does not mean the underlying goal is invalid. It means the
system must translate the term into observable criteria before acting.

## Example

Bad:

    make everything fully complete

Precise:

    subject: current repository branch
    action: implement missing testable modules
    scope: research + mobile operator layer
    inputs: current branch files and CI results
    constraints: no secrets, no irreversible external actions
    evidence: deterministic tests + CI
    acceptance: all named tests pass and CI reports success
    time: one bounded execution cycle
    authority: repository write authority only

## Core rule

    UNKNOWN > invented interpretation

The system should ask for, derive, or preserve missing specification rather than
quietly filling the gap with arbitrary assumptions.
