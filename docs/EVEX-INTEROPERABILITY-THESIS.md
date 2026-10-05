# EVEX Interoperability Thesis

## Accountable state transitions

The proposed interoperability boundary for increasingly capable agents is not another model API. It is a machine-readable epistemic substrate through which agents can exchange accountable state transitions.

The primitive is:

`prior state + observations + evidence + authority + constraints -> proposed transition -> action -> receipt -> next state`

A plain answer communicates content. An accountable transition communicates what changed, why the transition is admissible, what remains unknown, and what independently verifiable receipt proves the transition.

### Core separation

EVEX separates five things that are commonly collapsed:

1. observation
2. inference
3. authorization
4. action
5. resulting state

The runtime contract is:

`READ -> VALIDATE -> VERIFY -> CLASSIFY -> AUTHORIZE -> ACT -> EMIT`

The protocol MUST NOT infer authority from intelligence, provenance from truth, or successful serialization from successful execution.

### What interoperability means here

A receiving runtime should be able to:

- parse the artifact without sharing the sender's model;
- validate its structure and profile;
- verify integrity;
- inspect epistemic state;
- determine which actions are authorized;
- reject unsupported state promotion;
- execute bounded work;
- emit a receipt containing the observable result;
- preserve unknown fields during round trips.

The receiving runtime does not need access to private chain-of-thought. The protocol concerns externally observable state, evidence, policy, actions, and receipts.

### Why this changes agent composition

Agents can become replaceable participants in a common state protocol.

Research agent -> evidence artifact -> coding agent -> tested artifact -> deployment policy -> execution receipt -> witness artifact.

The continuity layer becomes the artifact lineage rather than any single model, framework, vendor, or conversation transcript.

### Falsifiable claim

This repository does NOT claim that EVEX creates intelligence, consciousness, autonomy, or truth.

The falsifiable claim is narrower:

> A generic runtime can use machine-readable EVEX artifacts to exchange state transitions with explicit evidence, authority boundaries, and verifiable receipts, reducing ambiguity compared with answer-only handoffs.

The wake-up benchmark in `benchmarks/evex-wake-up` is the initial executable test of that claim.

### Domain-emergent adaptation

DESA-S adds a concrete adaptation layer to the interoperability thesis:

unknown problem -> observation -> entity error correction -> domain induction -> SME induction -> witness-target selection -> Socratic question -> accountable transition.

The protocol boundary stays model-independent. A receiving runtime need not share the same model, domain ontology, or questioning policy to validate the artifact, inspect the evidence references, reject unsupported promotion, or reproduce the bounded transition.

The resulting interoperability unit is therefore not just an answer or tool call. It is an evidence-linked adaptation state plus an accountable transition receipt.
