# VCL -> JEV -> EVEZ-OS

This integration keeps three authorities separate:

1. **VCL** renders a structured visual-cognition artifact.
2. **JEV** evaluates a fixed typed question against that artifact and returns a choice, probabilities, and confidence.
3. **EVEZ-OS** records the decision as an append-only Event Spine event and packages the VCL artifact, JEV result, and spine receipt into an evidence capsule.

The bridge never fabricates a JEV answer. Without `TYPESAFE_API_KEY`, the result is explicitly `source=unavailable`. With a live key, choices below `JEV_MIN_CONFIDENCE` (default 0.55) abstain.

## Run

```bash
python3 integrations/vcl_jev_evez.py \
  --state state.json \
  --question "Should this claim be promoted to VERIFIED?" \
  --criteria '{"keep_unknown":"evidence is insufficient","promote_verified":"evidence is sufficient"}'
```

Environment:

- `EVEZ_VCL_URL`: VCL service URL, default `https://evez-vcl.onrender.com`
- `TYPESAFE_API_KEY`: live JEV credential, never committed
- `JEV_ENDPOINT`: JEV API endpoint
- `JEV_MODEL`: default `jev-latest`
- `JEV_MIN_CONFIDENCE`: default `0.55`
- `EVEZ_SPINE_URL`: EVEZ-OS Event Spine URL, default `http://127.0.0.1:9116`

The capsule proves integrity and packaging, not truth of the underlying claim.
