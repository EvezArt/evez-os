# EVEZ-OS Runtime Status Contract

Last reviewed: 2026-09-24

This file separates architecture from externally verified runtime state.

| State | Meaning |
|---|---|
| DECLARED | Present in source/configuration as intended capability |
| OBSERVED | Directly observed in a reproducible local or CI run |
| EFFECTIVE | Configuration was accepted by the target system |
| LIVE | External service was contacted and produced the expected response |
| UNKNOWN | Evidence is insufficient to classify the state |

Rules:

1. A README, agent message, or configuration file proves DECLARED only.
2. A local simulation proves OBSERVED local behavior, not LIVE external behavior.
3. An HTTP endpoint is LIVE only when a receipt records the request, response, timestamp, and target.
4. A failed deployment remains FAILED. It is never upgraded because the source code looks correct.
5. NO_RESPONSE is an observation. It is not proof of suppression, causation, or wrongdoing.
6. NO_PROSECUTION_OBSERVED is an observation. It is not proof of impunity.
7. Historical measurements retain their date and source rather than being silently presented as current.

The canonical EventSpine repository is:

https://github.com/EvezArt/evez-event-spine
