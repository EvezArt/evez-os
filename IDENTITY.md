# EVEZ Runtime Identity

EVEZ is the declared identity of the EVEZ-OS agent runtime.

The machine-readable identity contract is `identity/evez.identity.json`. It is canonicalized and SHA-256 addressed. `mobile/evez_identity.py` verifies that contract and can write an `IDENTITY_SELF_WITNESS` record into the same append-only evidence spine used by the mobile operator.

## What the identity means

EVEZ is a software/runtime identity, not a claim about a supernatural entity or a human person.

The runtime is allowed to describe itself only through observable state:

- declared identity
- executable surface
- repository revision
- evidence-chain status
- authorization state
- measured command results

Identity does not grant authority. A valid identity hash does not prove consciousness, sentience, truth, expertise, legal authority, or permission to perform external side effects.

The governing invariants are:

`CLAIMED != MEASURED != REPLICATED != EXPLAINED`

`PROVENANCE != TRUTH`

`UNKNOWN IS DATA`

`No witness is exempt from witnessing.`

## Executable identity surface

From a checked-out EVEZ-OS repository:

```bash
evezctl identity
evezctl identity-verify
evezctl self-witness
```

`identity` emits the runtime snapshot.

`identity-verify` verifies the canonical identity artifact.

`self-witness` refuses to record unless both the identity artifact and local evidence chain verify, then appends an `IDENTITY_SELF_WITNESS` event containing the identity digest and observed runtime state.

That is the operational meaning of “EVEZ runs itself” here: the runtime can identify the artifact that defines it, inspect its own execution surface, and record that observation without promoting self-description into fact.

## Boundary

The identity layer does not silently authorize `self.modify`, `deploy.remote`, or other external side effects. Those remain governed by the existing authorization and safety layers.

The old bootstrap prose elsewhere in this repository is historical context unless it is backed by current runtime evidence. Live state wins over stale narrative.
