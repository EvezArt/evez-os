# EVEZ Signal Negotiation

The signal domain is complete only when the system can answer which channels can
reach the operator now, which are consented, and what should be attempted first.

research/signal_negotiation.py provides that decision layer.

Each capability advertises:
- availability
- consent scopes
- attention estimate
- delivery reliability estimate
- cost
- maximum priority it can carry
- deterministic preference rank

The planner returns:
- READY
- DEGRADED
- NO_ELIGIBLE_CHANNEL

and an ordered fallback list.

For high-priority or explicitly redundant signals, multiple channels may be
selected. Every rendering keeps the same signal digest.

## Indelumvealoquivolution

evez-indelumvealoquivolution-v1 is the project namespace for adaptive
cross-modal representation. It means the representation can evolve according to
reachable and consented sensory interfaces without changing the underlying
signal identity or evidence lineage.

It is not a claim of an undocumented physical sense or hidden communications
channel.

## Delivery lifecycle

    PREPARE
      |
    RENDER
      |
    DELIVER
      |
    ACK

On failure:

    FALLBACK -> RENDER -> DELIVER -> ACK

An expired signal terminates at:

    EXPIRED

Every attempted delivery produces a deterministic receipt containing the signal
digest, channel, adapter, attempt number, timestamp, state, and outcome.

## Operator workflow

Termux can run:

    evezctl signal PACKET.json --auto --capabilities CAPABILITIES.json

Dry-run is the default.

Actual delivery requires:

    evezctl signal PACKET.json --auto --capabilities CAPABILITIES.json --deliver

A capability manifest is explicit operator configuration. The system never
grants consent merely because an adapter exists.
