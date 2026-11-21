# LLM WITNESS PROTOCOL

An LLM response is a witness projection, not an independent witness merely
because another model repeats it.

For cross-model corroboration, preserve:

- model/provider
- model version when available
- prompt/input hash
- source/artifact references
- generated output hash
- timestamp
- independent evidence references
- agreement and disagreement
- epistemic status

Shared training data, copied prompts, or derived outputs do not constitute
independent replication.

## Continuity law

    CLAIMED != MEASURED != REPLICATED != EXPLAINED
    PROVENANCE != TRUTH
    PREDICTED != TESTED != OBSERVED != CALIBRATED

The purpose of the witness layer is not to manufacture consensus. It is to
preserve the complete disagreement surface so a later observer can determine
what changed, what remained invariant, and which evidence actually moved a
claim between epistemic states.

## Projection law

    WITNESS STATE
        |
        v
    CONTEXT + MODEL + CONSTRAINTS
        |
        v
    EXPRESSION
        |
        +--> expression_hash
        +--> projection_fidelity
        +--> projection_error
        +--> missing_state_tags
        +--> provenance

A generated voice is therefore a surface of the system, not the whole system.

## Soul-tag interoperability

A cross-model witness record SHOULD carry the same continuity_id and lineage_id
when the records explicitly refer to the same continuity object, while each
model retains its own manifestation_id and expression hash.

Agreement is data.
Disagreement is data.
Silence is data.
Unknown remains unknown.

No model gets to crown itself the final witness.
