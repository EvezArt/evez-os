# Mobile-first engineering contract

EVEZ-OS is allowed to have large remote infrastructure, but the operator interface must fit inside a phone.

## Constraint-derived architecture

Local on Galaxy A16 / Termux:
- Git checkout
- evezctl
- small local logs
- shell/Python utilities
- evidence capture
- SSH client
- no required heavyweight build daemon

Remote:
- production services
- model inference
- databases
- object storage
- background jobs
- long-running simulations
- CI/CD
- observability

Source of truth:
- Git commits for code
- append-only spine for runtime events
- explicit status endpoints for current health
- CI for reproducibility
- deployment hooks for controlled promotion

## Operator loop

    IDEA
      |
      v
    phone -> git branch -> CI -> test
      |                    |
      |                    v
      +---------------> evidence
                           |
                           v
                      deploy hook
                           |
                           v
                    remote EVEZ mesh
                           |
                           v
                      health/status
                           |
                           v
                       spine event

A mobile-first system should degrade gracefully. Losing the phone must not lose the system.

### Offline evidence protocol

The operator has four distinct local states:

- **recorded**: an observation is present in the hash chain
- **queued**: the observation is waiting for remote delivery
- **delivered**: the remote endpoint returned a 2xx response
- **verified**: the local chain recomputes without a parent or digest mismatch

The outbox is deliberately at-least-once. A network failure never deletes an event. Remote delivery uses an `Idempotency-Key` based on the local event UUID, but actual server-side idempotency depends on the receiver. Losing the remote mesh must not erase the local evidence. Losing one service must not silently turn a failed run into a success.

## Evidence rule

Do not infer operational success from command completion. Capture the response, exit code, commit SHA, and timestamp. Treat DECLARED, MEASURED, and REPLICATED as different states.

## Security rule

Never put API keys in this repository. The Termux config contains only non-secret routing/configuration values. Remote credentials belong in the target environment's secret store.

## Why this matters

The phone constraint forces the architecture toward small commands, stable APIs, explicit state, and remote services that can be replaced without rebuilding the operator. That remains useful even when a full workstation becomes available.
