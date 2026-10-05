# EVEX Proof-Carrying Handoffs

## Problem

Traditional agent handoffs transfer instructions and context. They rarely transfer a machine-checkable statement of why the receiving agent is allowed to trust or act on the handoff.

EVEX adds that missing layer.

## Handoff contract

A proof-carrying handoff SHOULD include:

`intent + context hash + evidence refs + constraints + authority + required test + expected output`

Example:

```json
{
  "handoff_id": "ho-001",
  "intent": "classify_claim",
  "context_ref": "sha256:...",
  "evidence_refs": [
    "sha256:observation",
    "sha256:test"
  ],
  "constraints": {
    "allowed_states": ["UNKNOWN", "SUPPORTED", "CONTRADICTED"],
    "forbidden_actions": ["external_write"]
  },
  "authority": {
    "capability": "deterministic.classify",
    "policy": "benchmark"
  },
  "required_test": "verify-observation-binding",
  "expected_output": "evex.receipt.v1"
}
```

## Receiver behavior

A receiver MUST be able to reject the handoff for:

- invalid schema;
- failed integrity verification;
- unavailable evidence;
- insufficient authority;
- disallowed action;
- missing acceptance test;
- attempted epistemic upgrade without a permitted basis.

The receiver should not need to trust the sender's natural-language explanation.

## Why proof-carrying matters

This enables heterogeneous composition:

`Model A -> EVEX handoff -> Model B -> EVEX receipt -> Model C`

Each model can be changed independently while the handoff semantics remain addressable.

The artifact is the contract. The model is the participant.

## Security boundary

Proof-carrying does not mean cryptographic truth.

Cryptographic integrity can establish that bytes or canonical records were not changed after sealing. It cannot establish that an external observation was honest or that an inference is scientifically correct.

Applications requiring stronger guarantees must bind evidence to appropriate authorities, sensors, logs, signatures, attestations, or independent tests.
