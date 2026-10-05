# PERMALOOT

PERMALOOT is the recursive acquisition layer for EVEZ-OS.

It takes observable loot and repeatedly acquires structure from that loot:

```
RAW OBSERVATION
      ↓
DERIVED STRUCTURE
      ↓
META DISCOVERY
      ↓
BOUNDARY DISCOVERY
      ↓
NEXT FRONTIER
      ↓
next surge
```

The acquisition surge is intentionally non-terminating with respect to
repetition. Repeated structures are recorded as resonance rather than silently
discarded. The actual recursion is bounded by an explicit depth parameter so
the runtime cannot explode without limit.

The distinction is critical:

ACQUIRED != DERIVED
DERIVED != VERIFIED
NEXT_FRONTIER != OBSERVED

PERMALOOT acquires everything legitimately observable from its supplied input.
It does not acquire hidden system prompts, private reasoning, credentials,
protected platform metadata, or other information not present in the runtime's
authorized input surface.

## CLI

```bash
python mobile/evez_permaloot.py mobile/value-context.example.json --depth 6
python mobile/evez_permaloot.py mobile/value-context.example.json --response @response.txt --depth 6
```
