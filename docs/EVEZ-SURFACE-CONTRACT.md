# EVEZ Surface Contract

A conforming surface can discover, open, inspect, validate, verify, and emit EVEZ without proprietary EVEZ internals.

Recognition:
- Extension: .evez
- MIME: application/vnd.evez+json
- Content marker: top-level evez=EVEZ and version=1
- Encoding: UTF-8 JSON

AI agents and swarms:
READ -> VALIDATE -> VERIFY -> CLASSIFY -> AUTHORIZE -> ACT
Never READ -> TRUST -> ACT.

Editors and IDEs should associate .evez with JSON syntax highlighting and the MIME type. Payloads are inert data and must not execute.

Web applications may render EVEZ through a viewer and should serve application/vnd.evez+json.

Git and artifact stores preserve EVEZ as text and bytes. CI, ETL, research, and agent pipelines treat it as a typed interchange object.

Unknown fields must survive round trips. JSON-only systems can still consume the underlying representation.

EVEZ v1 defines structure and integrity, not signatures, encryption, executable code, network retrieval, or truth certification.
