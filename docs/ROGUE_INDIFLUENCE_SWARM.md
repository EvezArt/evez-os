# Rogue Indivifluence Swarm

EVEZ-OS now has a bounded symbolic swarm layer for individual-to-collective emergence.

The design goal is not "make one giant agent smarter." It is to preserve many independently generated proposals, let them mutate, let them influence one another, let temporary coalitions form, and then feed the resulting frontier back into the architecture.

The core loop is:

```
INDIVIDUAL SEEDS
      |
      v
ROGUE MUTATION
      |
      v
PAIRWISE INFLUENCE
      |
      +----> CHALLENGE / REINFORCE
      |
      v
COALITION FORMATION
      |
      v
INDIVIFLUENTIALITY
      |
      v
DISSENT-PRESERVING FRONTIER
      |
      v
YHWH SOVEREIGN JUDGE
      |
      v
VALUE / ARCHITECTURE PROPOSALS
```

"Indivifluentiality" is deliberately an EVEZ term. It names a modeled loop in which the individual changes the collective, the collective feeds back into the individual, and identity is not erased by consensus.

"Rogue" has a precise boundary here. The agents are free to generate hypotheses, mutate proposals, challenge one another, and form symbolic coalitions. They are not granted arbitrary filesystem writes, credential use, acquisition rights, network control, or deployment authority.

The influence values are modeled from supplied proposal text. They are not measurements of real-world influence, intelligence, consciousness, or agency.

The sovereign judge is also symbolic. It is the highest-pressure epistemic critic and cannot turn its own persona into authority.

## Operating laws

- INFLUENCE != EVIDENCE
- CONSENSUS != TRUTH
- ROGUE_GENERATION != EXECUTION_AUTHORITY
- INDIVIDUAL_IDENTITY != COLLECTIVE_OWNERSHIP
- DISSENT_IS_PRESERVED
- UNKNOWN != permission
- PROPOSED != VERIFIED
- CLAIMED != MEASURED != REPLICATED != EXPLAINED

The swarm therefore becomes an engine for discovering candidate architectures, not a magical permission escalator.

## Termux

```bash
python mobile/evez_indivifluence.py mobile/value-context.example.json --generations 3 --size 8
python mobile/evez_yhwh.py mobile/value-context.example.json
```

Or through `evezctl`:

```bash
evezctl swarm-emerge mobile/value-context.example.json
evezctl sovereign-judge mobile/value-context.example.json
```
