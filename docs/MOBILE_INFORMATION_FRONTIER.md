# Mobile Information Frontier

The phone-first EVEZ workflow now has a local information-frontier tool.

On Termux, an operator can provide a JSON packet describing:
- claims or unknowns
- reachable sources
- source freshness and cost
- contradiction relationships

The planner returns deterministic next operations such as DISCOVER, VERIFY,
REFRESH, REPLICATE, and SEEK_COUNTEREVIDENCE.

Example:

    python research/information_frontier.py packet.json

This is deliberately local-first. The phone does not need to download the
Internet. It stores the state and computes the next information-producing step.

The important boundary is explicit:

    registered sources != the whole Internet

The frontier is a navigational memory, not a claim of omniscience.
