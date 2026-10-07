# EVEZ Swarm Shared Self-Observation

The swarm must be able to inspect the state that governs the swarm.

This is a **shared read-only operational view**, not hidden chain-of-thought.

Visible to swarm members:
- agent identity and role
- trust/load/report/contradiction counters
- latest aggregate decision
- explicit UNKNOWN/uncertainty state
- whether contradictory evidence occurred
- aggregate coherence/resilience/evidence metrics
- authority boundaries

Explicitly not exposed:
- credentials
- private keys
- execution handles
- deployment authority
- hidden reasoning traces

The view is canonicalized and hashed.

A repeated deterministic simulation with identical inputs must reproduce the
same digest.

The principle is:

    opaque internal reasoning
        !=
    hidden operational state

A swarm cannot self-correct what its members are forbidden to observe.

The shared view therefore exposes enough state for:
- fault isolation
- role-aware coordination
- contradiction discovery
- evidence inspection
- deterministic replay

without granting any new execution authority.
