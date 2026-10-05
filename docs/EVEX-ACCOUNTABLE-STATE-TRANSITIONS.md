# EVEX Accountable State Transitions

## Purpose

An accountable state transition is a typed change from one recorded state to another where the transition declares:

- the prior state identity;
- the observations used;
- the evidence references;
- the epistemic classification;
- the authority boundary;
- the requested action;
- the acceptance test;
- the resulting state;
- a receipt for what actually happened.

The protocol deliberately keeps `CLAIMED`, `MEASURED`, `REPLICATED`, and `EXPLAINED` distinct.

## Transition object

A state transition SHOULD contain:

```json
{
  "transition_id": "tr-...",
  "parent_state_hash": "sha256:...",
  "classification": {
    "state": "SUPPORTED",
    "basis": ["obs-1", "test-1"]
  },
  "authority": {
    "capability": "deterministic.classify",
    "policy": "local-benchmark"
  },
  "action": {
    "type": "emit_receipt",
    "input_hash": "sha256:..."
  },
  "acceptance": {
    "tests": ["sha256-identity-check", "required-fields"]
  },
  "result": {
    "status": "SUCCEEDED",
    "observations": ["obs-2"]
  },
  "new_state_hash": "sha256:..."
}
```

The exact JSON shape for reusable implementations is defined in `schemas/evex-state-transition-v1.schema.json`.

## Invariants

A compliant runtime MUST preserve these boundaries:

- integrity does not prove truth;
- provenance does not prove truth;
- a claim does not become verified because it is repeated;
- a proposal does not become permission;
- a capability declaration does not prove effective capability;
- an action receipt records execution, not moral or factual correctness of the underlying claim;
- unknown fields survive round trips;
- payloads are inert data unless a separately authorized runtime interprets them.

## State promotion

The protocol supports explicit state promotion but never implicit promotion.

For example:

`UNKNOWN -> SUPPORTED`

requires an admissible basis defined by the profile or application policy.

A runtime MUST NOT silently perform:

`UNKNOWN -> VERIFIED`

because an upstream agent asserted the claim with confidence.

## Contradiction

Conflicting observations are first-class state.

A contradiction record SHOULD identify:

- competing claim or state identifiers;
- conflicting observations;
- scope;
- the test required to distinguish the alternatives;
- the current epistemic classification.

Contradiction is therefore a control input for the next experiment, not an error that must be hidden from downstream agents.

## Reproduction

A transition can be reproduced when another runtime receives the same canonical input, deterministic transformation, and acceptance criteria.

The expected outcomes are:

- `REPRODUCED`
- `DIVERGED`
- `INACCESSIBLE`
- `UNKNOWN`

A non-reproducible result is evidence about the transition, not proof that the original runtime was dishonest.

## DESA-S adaptation transitions

DESA-S uses the existing state.transition object with an explicit adaptation extension.

The extension binds the transition to a domain-state hash, SME-profile hash, selection-receipt hash, question identifier, and selected target. These fields make the adaptation decision portable without turning inference into authority.

A DESA-S transition SHOULD preserve:

- the full selection receipt or its content-addressed reference;
- rejected candidate targets;
- the targeter's self-inclusion result;
- the proposed question and its epistemic state;
- the domain and SME state hashes;
- the acceptance tests that prevent unsupported epistemic promotion.

The schema extension is defined in schemas/desas-evex-transition-v1.schema.json.
