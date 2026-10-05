# EVEZ Evidence Capsules

An evidence capsule is a portable provenance package.

It bundles source artifacts without silently rewriting them. Each embedded artifact retains its original bytes, size, encoding, and SHA-256 digest. The capsule also carries a SHA-256 digest over its complete canonicalized structure.

The capsule proves only integrity and packaging:

\`CAPSULE_INTEGRITY != CLAIM_TRUTH != EXPLANATION\`

## Build

From the repository root:

~~~bash
python evidence/evidence_capsule.py build capsule.json \
  claim=research/claim-packet.json \
  fusion=civic/fusion.json \
  swarm=research/swarm-result.json \
  review=research/review.json \
  --metadata '{"purpose":"evidence review"}'
~~~

Or through the mobile operator:

~~~bash
evezctl capsule-build capsule.json \
  claim=research/claim-packet.json \
  fusion=civic/fusion.json \
  swarm=research/swarm-result.json
~~~

## Verify

~~~bash
python evidence/evidence_capsule.py verify capsule.json
~~~

or:

~~~bash
evezctl capsule-verify capsule.json
~~~

Verification must fail if an embedded artifact, manifest field, or capsule body has been tampered with.

## Recommended contents

A useful capsule can contain:

- source extracts or normalized source reports
- cross-source fusion output
- a deterministic swarm/anomaly run
- an epistemic evaluator result
- signed authority envelopes where governance matters
- a human review note

The capsule is not a truth certificate. It is a tamper-evident transport container for evidence and analysis.
