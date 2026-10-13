# Bounded Reality Substrate Cycle 2026-10-07

## Gap target

The missing layer between EVEZ cognition and persistent world representation was
identified as a lack of shared contracts for:

- world entities
- causal events
- replayable snapshots
- multimodal projection manifests
- explicit counterfactual branches
- cultural lineage and mutation
- self-prediction error
- resource-aware next-operation selection

## Implemented

- research/reality_substrate.py
- research/test_reality_substrate.py
- mobile/evez_reality.py
- mobile/test_evez_reality.py
- docs/REALITY_SUBSTRATE.md
- docs/GOD_DIRECTOR.md
- mobile/evezctl reality
- bounded-kernel CI coverage for the new substrate

## Core invariant

World state is the source model.

Media is a projection.

Simulation is not observation.

A director is not an authority.

## Compound loop

intent
-> state
-> event
-> snapshot
-> projection
-> observation
-> event

## Compounding units

CulturalUnit provides explicit ancestry and mutation tracking.

SelfMetric records predicted versus observed behavior and resource cost.

DirectorCandidate exposes expected information gain, expected value, risk, and
resource cost, then chooses deterministically without self-authorization.

## Verification boundary

The branch is ready for independent CI evaluation.

Do not infer green status until the GitHub check results are actually emitted
for the new head.
