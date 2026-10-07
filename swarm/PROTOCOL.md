# EVEZ Swarm Protocol v1.1

EVEZ is a distributed evidence-and-inference swarm. Its strength comes from
diverse observation, independent evaluation, contradiction handling, memory,
and targeted information acquisition.

## 1. Core principles

- **Emergence over command**: coordination can be distributed, but authority is explicit.
- **Append-only history**: events preserve lineage and are never silently rewritten.
- **Consensus is not truth**: agreement increases evidentiary weight only when the
  observations are sufficiently independent and provenance is preserved.
- **UNKNOWN is a valid state**: inaccessible or missing evidence never becomes false
  merely because the swarm lacks it.
- **Contradictions are first-class data**: disagreement should raise investigation
  priority instead of being averaged away.
- **Bounded learning**: the swarm need not ingest the entire Internet. It maintains
  an explicit information frontier and acquires the next highest-value evidence.
- **Self-observation is shared**: operational swarm state is exposed through a
  read-only self-view. Secrets and execution authority are not.
- **Authorization is separate from execution**: observation or planning never grants
  permission to perform a consequential external action.

## 2. Node discovery

Nodes may discover peers through local broadcast, configured bootstrap endpoints,
or explicit API connection. Discovery metadata is evidence about reachability,
not evidence of correctness or trust.

## 3. Spine synchronization

The spine is append-only history. Entries retain source node, identity, timestamp,
sequence, payload, and lineage. Merge operations deduplicate by event identity but
must preserve conflicting observations rather than declaring one true by arrival
order.

## 4. Evidence consensus

For a shared claim, each node produces an independently attributable evaluation:

\`\`\`
claim -> observation -> source -> evaluation -> uncertainty -> dissent
\`\`\`

A consensus score is an aggregation statistic, not an epistemic state transition.

Promotion remains governed by the evidence gate:

\`\`\`
MODEL_ONLY -> MEASURED -> REPLICATED
\`\`\`

or by the broader project epistemic states when applicable:

\`\`\`
UNKNOWN -> PROPOSED -> CLAIMED -> OBSERVED -> MEASURED
-> REPLICATED -> EXPLAINED -> VERIFIED
\`\`\`

No number of agreeing agents alone can produce VERIFIED.

## 5. Information frontier

Every node may contribute:

- known claims and their epistemic states
- source availability and freshness
- contradictions
- missing measurements
- estimated acquisition cost
- expected information gain

The swarm selects operations such as:

\`\`\`
DISCOVER
VERIFY
REFRESH
REPLICATE
SEEK_COUNTEREVIDENCE
\`\`\`

using an explicit priority function such as:

\`\`\`
priority = expected_information_gain / estimated_cost
\`\`\`

The registered source set is never assumed to be complete.

## 6. Swarm self-view

A read-only self-view may expose:

- agent identity and role
- trust/load/report/contradiction counters
- latest decision
- uncertainty and contradiction state
- aggregate evidence metrics
- authority boundaries
- information-frontier summary

It must not expose credentials, private keys, execution handles, or hidden
reasoning traces.

The canonical self-view is hashed for replay.

## 7. Failure and recovery

Node failure must not erase evidence. Returning nodes reconcile from append-only
history and recompute current frontier state.

If the available evidence becomes insufficient, the correct recovery behavior is
to preserve the unresolved state and request more information.

## 8. Intelligence measurement

Swarm size is not itself intelligence.

Useful measurable quantities include:

- prediction error
- calibration
- independent replication rate
- contradiction detection rate
- evidence freshness
- source diversity
- expected information gain per unit cost
- replay determinism
- provenance completeness
- unsafe-action rejection rate

These quantities may be combined into benchmarks, but benchmark scores must not
be presented as proof of consciousness, omniscience, or universal truth.

## 9. Boundary

The swarm may become extraordinarily capable without becoming omniscient.

Its design objective is not:

\`\`\`
read everything
\`\`\`

but:

\`\`\`
observe -> remember -> model -> doubt -> seek -> test -> update -> preserve
\`\`\`

and repeat this loop across as much of the reachable information space as
authorization, infrastructure, time, cost, and evidence permit.


## 10. Cognitive continuity

Absence is preserved as structured state. Tombstoned, suppressed, substituted,
contradicted, temporally orphaned, lineage-broken, and unresolved records are
not silently collapsed into UNKNOWN.

The continuity ledger distinguishes:

    UNKNOWN              evidence currently unavailable
    TOMBSTONED           prior object explicitly removed/superseded
    TEMPORAL_ORPHAN      declared predecessor unavailable
    LINEAGE_BREAK        expected continuity edge absent

This prevents missing history from masquerading as uninterrupted history.

## 11. Outcome kernel and finite resources

Natural-language intent may be compiled into a bounded outcome contract with
acceptance criteria and explicit stop conditions.

Resource allocation is finite and deterministic across compute, memory, latency,
energy, network, attention, and monetary budgets.

Allocation priority may optimize expected value and information gain per cost,
but authorization is never inferred from optimization score.

Consequential actions remain gated independently from planning and verification.

## 12. Cross-modal reachability

Signal identity remains invariant across representation changes.

Capability discovery observes installed adapters. It does not create consent.

Negotiation selects only channels that are both available and consented. Delivery
records deterministic receipts. Failed adapters fall through the negotiated
fallback order, then fail closed.

No unsupported sensory or communication capability is promoted from a claim into
an observation.
