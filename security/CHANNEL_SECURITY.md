# EVEZ Defensive Channel Security

This is a defensive control model for EVEZ-OS. It is not a military communications system.

## Channel classes

| Channel | Purpose | Minimum control |
|---|---|---|
| COMMAND | human-directed actions | authenticated identity, authorization policy, signed request, human approval |
| TELEMETRY | health and sensor reports | source authentication, integrity checks, timestamps |
| EVIDENCE | immutable observations | canonical records, hash chaining, verification |
| DEPLOYMENT | software promotion | provenance, manifest verification, dual control |
| EMERGENCY | recovery/break-glass | bounded TTL, explicit reason, append-only record, post-event review |

## Never trust the channel because it exists

The channel itself is not an authority.

A message can be:
- authentic but unauthorized
- authorized but stale
- signed but replayed
- internally consistent but factually wrong
- delivered successfully but not actually applied

The agent must distinguish those states.

## Agent safety ceiling

The autonomous agent cannot:
- assign itself a military rank
- represent itself as a Soldier
- submit a military enlistment application as though it were a human
- grant itself a clearance
- acquire human command authority
- silently bypass dual-control policy
- convert synthetic qualification into real-world authority

It can:
- collect evidence
- run defensive tests
- detect violations
- prepare qualification packets
- recommend actions
- request human approval
- prove whether its own claimed competency evidence is internally consistent
- refuse unsafe or unauthorized operations
