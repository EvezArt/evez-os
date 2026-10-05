# Counterfactual Threat Map

This module exists to enforce one distinction:

> anomaly is not coordination.

A burst can be produced by one operator, CI, scheduled automation, retries,
mirrors, or generated activity. The detector therefore requires:

1. independent actors,
2. independent sources,
3. a timing/shape deviation,
4. survival of actor-permutation null tests.

The output is an evidence state, not an accusation.

States:

- `SUPPORTED_COORDINATION_SIGNAL`
- `ANOMALY_REQUIRES_REVIEW`
- `ANOMALY_NOT_COORDINATION_EVIDENCE`
- `NO_COORDINATION_SIGNAL`
- `UNKNOWN`

The detector deliberately does not infer motive, paymasters, identity guilt, or
hostile intent. Those require independent evidence outside this statistical layer.

This is the breakthrough layer for the EVEZ threat-map architecture because it
turns "that looks coordinated" into a falsifiable test.
