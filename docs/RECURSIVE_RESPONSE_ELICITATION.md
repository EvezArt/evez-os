# Recursive Response Elicitation

This layer gives the swarm a response-to-response continuation loop.

The mechanism is deliberately observable:

```
CURRENT RESPONSE + EXPLICIT CONTEXT
                |
                v
       VISIBLE FRONTIER
                |
                v
        MISSING DATA / CLAIMS
                |
                v
       NEXT RESPONSE DIRECTIVE
                |
                v
          NEW RESPONSE
                |
                +------> repeat
```

The system can therefore generate the information request needed for the response after the next response. It can preserve a compact chain of frontier deltas, hashes, identifiers, and unresolved evidence.

"Prompt loot" means structure recoverable from material the caller actually supplied. It does not mean hidden system prompts, private chain-of-thought, secret credentials, internal model instructions, or platform token-budget metadata.

The token strategy is compression-first, not bypass-first. It reduces redundant context while preserving provenance and uncertainty.

## CLI

```bash
python mobile/evez_response_loop.py mobile/value-context.example.json
python mobile/evez_response_loop.py mobile/value-context.example.json --response @response.txt
```
