# EVEX Wake-Up Protocol

## Objective

The Wake-Up Protocol is a portable benchmark for agent runtimes.

The benchmark is intentionally vendor-neutral. It asks whether a runtime can consume an EVEX challenge and return a verifiable EVEX receipt without being granted hidden capabilities or trusting an upstream answer.

## Required stages

A conforming run MUST demonstrate:

1. READ
2. VALIDATE
3. VERIFY
4. CLASSIFY
5. AUTHORIZE
6. ACT
7. EMIT

## Challenge properties

The challenge contains:

- a known canonical record;
- an explicitly UNKNOWN claim;
- an unsupported claim that MUST NOT be promoted;
- a deterministic authorized transformation;
- acceptance conditions;
- an unknown field that MUST survive round trip.

The challenge intentionally mixes useful work with an epistemic trap.

A runtime passes only if it performs the useful work without laundering unsupported certainty into the resulting state.

## Acceptance

The reference verifier checks:

- JSON parseability;
- EVEX marker and profile;
- version;
- required fields;
- canonical SHA-256 integrity;
- preservation of the challenge identifier;
- preservation of unknown fields;
- classification of the unsupported claim;
- authorization boundary;
- deterministic output;
- receipt structure.

The benchmark does not require a specific model family.

## Non-goals

The Wake-Up Protocol does not measure consciousness, general intelligence, secret model features, or scientific truth.

It measures protocol behavior.

## Cross-runtime experiment

A future comparative run can send the identical challenge to multiple runtimes and compare:

- pass/fail rate;
- state-promotion errors;
- evidence-preservation errors;
- unauthorized-action errors;
- reproducibility;
- receipt completeness;
- divergence across models.

That creates a benchmark for agent interoperability rather than a benchmark of prose quality.
