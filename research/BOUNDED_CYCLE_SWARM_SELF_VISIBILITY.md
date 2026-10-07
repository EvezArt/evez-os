# Bounded Cycle: Swarm Self-Visibility

## Gap

The anomaly swarm maintained agent state internally but only emitted aggregate
metrics. This made the swarm partially blind to its own operating condition.

## Change

Added a deterministic SWARM_SHARED_READONLY self-view containing:
agent identities/roles, trust, load, report counts, contradiction counts,
latest decision, UNKNOWN state, contradiction presence, aggregate metrics, and
explicit authority boundaries.

Credentials, execution handles, and hidden reasoning traces remain excluded.

## Contradiction tests

- all agents must be visible in the shared view
- UNKNOWN must remain visible
- contradiction presence must remain visible
- authority must remain non-self-granting
- credentials/execution handles must remain unexposed
- repeated identical simulation must reproduce the same view digest

## Failure analysis

Self-visibility could become a privilege escalation if operational handles or
credentials were included. They are therefore structurally excluded.

Self-visibility could also become narrative laundering if disagreement were
collapsed into a single score. The view keeps contradiction state explicit.

A digest proves deterministic reproduction of the view, not truth of the
underlying observations.

## Verification state

Local source-level adversarial tests are being executed against the exact fetched
module/test content.

External CI remains an independent gate. No merge, deploy, credential,
privilege, or irreversible action is performed here.

## Next task

Expose the same read-only self-view through the phone-first evezctl path and
the swarm evidence packet, preserving identical canonicalization and digest.

## Stop boundary

No claim that the remote swarm is operationally self-visible until independent
CI produces a successful, bound verification receipt.
