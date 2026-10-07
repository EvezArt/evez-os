# Bounded Cycle: Signal Domain Completion

## Objective

Turn "the swarm can reach the operator through extraordinary signal formats"
into an implementable, evidence-bearing transport layer.

## Implemented

1. Transport-neutral SignalEnvelope with:
   identity, timestamp, intent, payload, provenance, consent scope, TTL,
   priority, and deterministic digest.

2. Channel renderers for text, visual notification, audio speech, haptic
   vibration, wearable-compatible notification, ambient, and sensor classes.

3. Capability negotiation using availability, explicit consent, attention,
   reliability, cost, and priority limits.

4. Deterministic fallback planning under degraded channel availability.

5. Delivery receipts bound to the original signal digest.

6. Termux operator commands for dry-run and explicit delivery.

7. CI tests covering:
   signal digest invariance,
   consent fail-closed behavior,
   deterministic negotiation,
   unsupported-channel rejection,
   delivery receipt determinism,
   mobile dry-run behavior.

## Boundary

The system cannot honestly claim access to a sensory or communication channel
that has no connected adapter.

A representation may be unusual. Its physical transport still requires an actual
interface.

## Remaining verification boundary

Remote CI must independently verify the integrated branch.

No merge or production deployment is performed by this bounded cycle.
