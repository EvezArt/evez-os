# EVEZ Cross-Platform Runtime Bus

Canonical service roles:

- VCL browser runtime: https://github.com/EvezArt/evez-vcl/blob/main/demos/evez-chatgpt-runtime.html
- VCL Core: https://evez-vcl-core-8123c7mc0-evezx.vercel.app
- EVEZ-OS: https://evez-fh8dnmlf8-evezx.vercel.app
- EVEZ-Claw: https://evez-claw-3gvtxb5cj-evezx.vercel.app
- AGI pipeline: https://evez-agi-pipeline-v3-i5beclljo-evezx.vercel.app

Protocol: evez-runtime-v1.

Every message carries source, target, kind, id, timestamp, trace ID and payload. URLs identify routes; they do not prove health. Probe /health where available and record the result. Never place secrets in bus URLs.

This manifest is a routing contract only. Provider deployment state, runtime health and backup health are separate evidence classes.
