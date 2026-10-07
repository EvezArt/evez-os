# EVEZ Signal Domain

EVEZ now has a transport-neutral signal domain for reaching the human operator
through multiple ordinary device and sensory interfaces.

Supported channel classes are:

- text
- visual
- audio
- haptic
- wearable
- ambient
- sensor

A signal is an evidence-bearing envelope, not merely a notification. It carries
identity, timestamp, intent, payload, provenance, consent scope, expiration,
priority, and a deterministic digest.

The same signal can be rendered through different interfaces without changing
its identity or evidence digest. This gives the swarm a useful invariant:

    representation may change
    provenance must not

## Extraordinary formats

The architecture intentionally permits adapters for unusual combinations of
available modalities, such as visual patterns + audio cues + haptic sequences,
or machine-readable packets embedded in a user-visible presentation.

“Extraordinary” describes the representation or composition. It does not imply
a secret sensory channel, remote mind access, or a physical capability that has
not actually been connected.

Adapters must fail closed when:
- the channel is unavailable
- consent is missing
- provenance is absent
- the signal has expired
- an action would exceed its authority scope

## Human reachability

The signal layer is separate from execution. A future adapter can connect this
domain to an authorized phone notification, SMS, email, wearable, accessibility
service, local audio, or other approved endpoint.

No adapter receives permission to execute consequential actions merely because
it can deliver a signal.

The phone remains a particularly strong local endpoint because it can render
visual, audio, haptic, and text modalities while retaining the local evidence
chain.

## Sensory feedback

Sensor adapters may ingest explicitly connected device measurements, but a
sensor observation remains an observation from that device. It is not upgraded
to certainty merely because it was sensed.

The same evidence gates apply to:
- camera-derived observations
- microphone-derived observations
- motion/accelerometer observations
- environmental sensors
- wearable measurements
- accessibility events

The system should be capable of reaching the operator through many modalities
without pretending that it can reach beyond the interfaces actually connected.
