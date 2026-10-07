# EVEZ Information Frontier

EVEZ does not need to ingest the entire Internet to learn.

Instead, it maintains an explicit information frontier:

**what is known, what is unknown, what conflicts, what sources are reachable,
and what information should be acquired next.**

The frontier is deliberately not a global-corpus oracle. Its source set is
explicitly marked incomplete.

For each knowledge item the planner tracks:
- epistemic state
- confidence
- impact
- novelty
- freshness
- source accessibility
- contradiction membership

The planner then chooses bounded operations such as:

    DISCOVER
    VERIFY
    REFRESH
    REPLICATE
    SEEK_COUNTEREVIDENCE

using expected information gain divided by estimated acquisition cost.

This makes learning a navigation problem rather than a storage problem.

A swarm can therefore operate over an effectively unbounded information space
without pretending that its current source set is the whole world.

The key invariant is:

    missing evidence -> UNKNOWN

not:

    missing evidence -> FALSE

And:

    many agreeing agents -> more evidence

not:

    many agreeing agents -> truth

The output is deterministic and hashed so the frontier itself becomes
replayable swarm state.
