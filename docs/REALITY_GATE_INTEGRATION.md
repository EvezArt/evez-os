# Reality Gate Integration

EVEZ-OS exposes multiple autonomous services. The Event Spine remains the historical
record, but history alone does not authorize actions.

The Reality Kernel provides the procedural gate:

    request -> claim/evidence -> authority -> reversibility -> decision -> effect

Recommended service boundary:

- Event Spine (:9116): immutable audit history.
- Reality Gate: policy evaluation before consequential effects.
- Gateway (:9118): route requests, but do not self-authorize them.
- WITNESS/CAIN: preserve review and contradiction events.

Do not describe an agent's internal output as proof of consciousness, intent, or
truth. Record observable behavior and the evidence supporting any interpretation.

Reference:
https://github.com/EvezArt/evez-event-spine
