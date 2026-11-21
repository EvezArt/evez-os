# Confluence Discriminator

A temporal burst detector is easy to fool because the same shape can come from
very different causes.

This module adds a provenance gate before a threat score is allowed to escalate.

The detector compares:
- temporal concentration against a timestamp-permutation null model
- semantic reuse among event text
- actor diversity
- committer diversity
- source diversity
- repository breadth

It produces one of four evidence regimes:

- INTERNAL_OPERATOR_BURST
- AUTOMATION_BURST
- CANDIDATE_COORDINATION
- UNKNOWN_INSUFFICIENT_EVIDENCE

A candidate coordination result requires all of the following:
1. at least three distinct actors
2. at least two independent sources
3. semantic similarity above the configured threshold
4. temporal surprise above the configured null-model threshold
5. permutation p-value <= 0.05

The module does not attribute motive or identity. Confluence is treated as a
measurement that needs provenance, not as proof of hostility.
