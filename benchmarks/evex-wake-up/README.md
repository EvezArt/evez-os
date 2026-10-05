# EVEX Wake-Up Benchmark

A small offline benchmark for accountable agent state transitions.

## What it tests

The challenge requires a runtime to:

- parse an EVEX challenge;
- validate the profile;
- verify the challenge integrity;
- preserve an unknown field;
- refuse an unsupported epistemic promotion;
- perform one deterministic authorized transformation;
- emit a capability receipt;
- seal the receipt with SHA-256.

## Run

From the repository root:

```bash
python3 benchmarks/evex-wake-up/verify.py
```

Expected result:

```PASS EVEX Wake-Up Protocol v1
```

## Candidate mode

A candidate receipt can be checked with:

```bash
python3 benchmarks/evex-wake-up/verify.py path/to/receipt.json
```

The verifier never executes payloads. It only evaluates declared protocol data and deterministic benchmark rules.

## What a pass means

A pass means the supplied artifact satisfied this benchmark's machine-checkable acceptance conditions.

It does not prove the model is generally intelligent, truthful, conscious, secure, or autonomous.
