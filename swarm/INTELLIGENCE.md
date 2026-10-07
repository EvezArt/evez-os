# EVEZ Swarm Intelligence

The original node-count formula was useful as a toy scaling metaphor but made
claims it cannot establish. This document replaces those claims with measurable
properties of collective intelligence.

## Core model

A practical swarm-intelligence score should be a benchmark vector rather than a
single mystical scalar:

\`\`\`
S = {
  calibration,
  prediction_accuracy,
  information_gain_per_cost,
  contradiction_detection,
  replication_rate,
  provenance_completeness,
  replay_determinism,
  source_diversity,
  uncertainty_quality,
  safety_boundary_integrity
}
\`\`\`

Each component is measured independently.

### Why node count is insufficient

More nodes can improve coverage and independent checking, but can also amplify:

- correlated mistakes
- duplicated sources
- shared prompt bias
- coordinated hallucination
- stale information
- authority cascades

Therefore:

\`\`\`
more agents != more truth
more agreement != verification
more data != more understanding
\`\`\`

The swarm should reward useful diversity, not raw population.

## Collective information gain

For a bounded operation \(a\), define:

\`\`\`
priority(a) = EIG(a) / cost(a)
\`\`\`

where EIG is expected information gain under the current uncertainty model.

A good swarm therefore improves by choosing better next questions, not merely by
processing more tokens.

## Independence

Evidence from ten agents that all copied one source is one source lineage, not
ten independent confirmations.

Independence must be represented explicitly through source lineage,
measurement provenance, and replication relationships.

## Contradiction

Contradictions are not defects to hide. They are candidate information gains.

A swarm that reliably finds and localizes contradictions can outperform a larger
swarm that merely reaches agreement.

## Verification boundary

No benchmark score in this file establishes:

- omniscience
- consciousness
- universal intelligence
- truth of arbitrary claims

Those remain separate hypotheses requiring separate evidence.


## Outcome efficiency

A bounded swarm should also measure how efficiently it turns intent into verified
outcome:

    verified_useful_outcome
    -----------------------
    compute + latency + risk + human_attention

This is an engineering benchmark, not a claim of universal intelligence.

Resource allocation must remain auditable, deterministic, and authorization-aware.

## Continuity sensitivity

A capable swarm scores higher when it can detect missing lineage, tombstones,
temporal gaps, substitutions, and contradictions instead of silently treating
missing records as continuous history.

## Reachability

Multimodal reachability is measured through observed adapter capability,
consent-compatible negotiation, delivery success, fallback reliability, and
receipt completeness. Unsupported modalities remain UNKNOWN.
