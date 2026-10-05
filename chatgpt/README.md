# ChatGPT bridge

Use the .evez.json alias when the receiving ChatGPT upload surface does not accept .evez.

Canonical:
artifact.evez

ChatGPT-compatible upload alias:
artifact.evez.json

The two files contain the same EVEZ v1 JSON bytes. The .json suffix exists only to pass upload extension gates.

## DESA-S and EVEX

DESA-S state can be carried as EVEZ JSON while its accountable state transition is carried as EVEX JSON.

Use examples/desas-socratious.evez for the evidence-bearing state and examples/desas-socratious.evex.json for the EVEX transition fixture.

A ChatGPT-compatible JSON surface should treat both as inert structured data, preserve unknown fields, verify integrity when present, and never promote UNKNOWN or PROPOSED merely because an AI artifact says so.
