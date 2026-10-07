# EVEZ Signal Domain

EVEZ has a transport-neutral signal domain for reaching the human operator
through multiple ordinary device and sensory interfaces.

Supported channel classes include:
- text
- visual
- audio
- haptic
- wearable
- ambient
- sensor

A signal carries identity, timestamp, intent, payload, provenance, consent scope,
expiration, priority, and a deterministic digest.

The same signal can be rendered through different interfaces without changing
its identity or evidence digest.

## Extraordinary formats

The architecture supports unusual compositions such as visual patterns plus
audio cues plus haptic sequences, or machine-readable content embedded in a
user-visible presentation.

Extraordinary refers to representation and composition. It does not assert a
secret sensory channel, remote mind access, or any physical capability that has
not actually been connected.

## Human reachability

Signal delivery is separate from execution authority.

Future adapters may connect the domain to authorized phone notifications,
SMS, email, wearables, accessibility services, local audio, or other approved
endpoints.

No delivery adapter grants permission to execute a consequential action.

## Sensory feedback

Sensor adapters may ingest explicitly connected device measurements. Those
measurements remain observations attributed to their device and provenance.

The evidence gates remain unchanged for:
camera-derived observations,
microphone-derived observations,
motion measurements,
environmental sensors,
wearables, and accessibility events.

## Signal identity invariant

    representation may change
    provenance must not

The digest therefore follows the signal across modality changes, negotiation,
fallback, and delivery receipts.
