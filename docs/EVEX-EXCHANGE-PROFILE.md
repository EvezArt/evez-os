# EVEX Exchange Profile v1

Status: PROPOSED

EVEX is the EVEZ Exchange profile for AI-to-AI and swarm interchange.

Canonical extension: .evex
ChatGPT-compatible upload alias: .evex.json
Media type: application/vnd.evez.exchange+json

EVEX is JSON-native. The outer object identifies EVEX; payload.exchange describes a bounded exchange contract.

Required top-level identity:
- evex = EVEX
- version = 1
- profile = evez.exchange
- kind
- id
- created_at
- state
- payload
- integrity

The exchange contract is deliberately inert. A consumer must not execute payload text merely because it arrived in an EVEX file.

Recommended processing:
READ -> VALIDATE -> VERIFY -> CLASSIFY -> AUTHORIZE -> ACT -> EMIT

EVEX does not confer authorization. It records what an exchange proposes or reports.

A JSON upload alias exists because ChatGPT currently supports JSON/text data files while not listing .evex as a native upload extension. The .evex and .evex.json files contain identical bytes.

EVEX is therefore a transport/profile for EVEZ evidence-bearing exchanges, not a claim that OpenAI has registered the extension natively.
