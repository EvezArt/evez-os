# Deterministic Intent Optimization

EVEZ intent optimization ranks explicit candidate interpretations without silently inventing the user's objective.

The runtime converts each candidate into a bounded intent vector:

- clarity
- specificity
- actionability
- evidence density
- urgency
- reversibility
- semantic complexity
- ambiguity
- risk
- information gap

The optimizer uses a deterministic weighted score. A vague candidate is blocked by the precision contract. A close top-two score remains AMBIGUOUS_TIE. A candidate without enough evidence remains EVIDENCE_GAP. Only a sufficiently differentiated candidate with adequate evidence becomes OPTIMIZED_CANDIDATE.

This is an internal optimization model, not a claim of objective human-intent measurement. When the runtime cannot justify a choice, it preserves the ambiguity instead of manufacturing certainty.
