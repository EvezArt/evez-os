# Anomaly + Adaptive Swarm Cognition Lab

This research runtime combines two questions that are usually kept separate:

1. How should a multi-agent system reason when its observations are incomplete, contradictory, noisy, or disconnected?
2. How should an agent handle genuinely unexplained observations without converting "unknown" into mythology?

## NHI / UAP boundary

NHI means non-human intelligence. In this repository it is an explicit hypothesis category, not a fact.

UAP reports are observations that remain unidentified under available evidence. NASA states that it has not found credible evidence of extraterrestrial life and that there is no evidence UAPs are extraterrestrial. NASA's UAP work emphasizes improving data collection and scientific analysis. AARO likewise has a formal mission to detect, identify, attribute, and mitigate anomalous phenomena near national-security areas.

Therefore the simulation keeps:

UNKNOWN
PROPOSED
SUPPORTED
VERIFIED

separate.

An observation may be strange without establishing an exotic cause.

## Swarm model

The simulation treats a fleet/armada as a distributed reasoning topology, not as a weapons controller.

Agents have bounded roles:
- SCOUT
- ANALYST
- WITNESS
- COORDINATOR

The stress modes are:
- clean
- noisy
- partitioned
- adversarial-noise

The latter means synthetic contradictory observations and decoy-like signals inside the simulation. It is not a model for attacking real systems.

## The actual objective

The swarm does not optimize for "winning" by defeating an opponent.

It optimizes for:
- coherent sensing
- evidence preservation
- recovery from degraded communications
- contradiction detection
- uncertainty retention
- bounded authority
- human command preservation

That creates a better definition of emergence:

    emergence =
        coherence
        + resilience
        + epistemic integrity
        ------------------------------------------------
                             3

A swarm that becomes extremely coordinated while becoming epistemically dishonest scores badly.

## The "already won" condition

The system is successful before the final decision when the architecture makes these invariants difficult to violate:

    UNKNOWN stays UNKNOWN until evidence changes it.
    A valid message is not automatically an authorized action.
    A signed claim is not automatically a true claim.
    A swarm cannot grant itself authority.
    Losing one channel does not erase history.
    Contradictions are recorded instead of harmonized away.
    Human command remains external to the model.

That is the metacognitive win-state.
