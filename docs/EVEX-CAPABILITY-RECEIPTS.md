# EVEX Capability Receipts

## Purpose

A capability declaration says what a runtime claims it can do.

A capability receipt records what it actually attempted and what happened.

That distinction is essential:

`DECLARED != EFFECTIVE`

A receipt SHOULD contain:

- capability identifier;
- runtime identity;
- policy decision;
- input hash;
- output hash;
- start and end timestamps where available;
- execution status;
- observable result;
- error classification where relevant;
- parent artifact or transition reference.

## Example

```json
{
  "receipt_id": "rcpt-001",
  "capability_id": "deterministic.sha256",
  "runtime": {
    "name": "evex-wake-up",
    "version": "1"
  },
  "policy_decision": "AUTHORIZED",
  "input_sha256": "sha256:...",
  "output_sha256": "sha256:...",
  "status": "SUCCEEDED",
  "observable": {
    "algorithm": "sha256",
    "match": true
  }
}
```

## Capability lifecycle

EVEX uses the following lifecycle as an application-level protocol pattern:

`DISCOVERED -> DECLARED -> PERMITTED -> TESTED -> EFFECTIVE -> COMPOSED -> VERIFIED -> PUBLISHED -> DEPRECATED/REVOKED`

A declaration alone does not skip stages.

## Capability composition

A composed capability inherits the weakest relevant evidence boundary unless stronger policy says otherwise.

For example:

`fetch -> parse -> classify -> write`

should not become an automatically trusted macro-capability merely because each component was individually declared.

The composition SHOULD carry references to the receipts or transition records that establish which stages actually occurred.

## Why receipts matter

Receipts create a machine-queryable answer to:

> What can this runtime actually demonstrate that it did?

That is a more operationally useful question than:

> What does this agent say it can do?
