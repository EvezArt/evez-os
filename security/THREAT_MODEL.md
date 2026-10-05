# EVEZ-OS Defensive Threat Model

This is a defensive engineering model, not a military certification.

## Adversary assumptions

Assume an attacker can:
- observe or modify network traffic
- replay captured requests
- modify local evidence files
- compromise a remote service without compromising the phone
- steal a bearer credential
- exploit a dependency or CI action
- cause network, service, or storage failure
- exploit operator mistakes

Do not assume:
- network location implies trust
- HTTP success proves desired state exists
- device ownership implies device trust
- a Git tag is immutable
- a source-embedded secret is safe
- a hash chain proves who created an event

## Controls

Identity: a device-local Ed25519 key signs operation envelopes.

Authorization: the action policy defaults to deny. Deployment requires explicit second-factor approval.

Evidence: canonical records are hash-linked and verification is fail-closed.

Replay resistance: operation envelopes get unique IDs and remote sync sends an Idempotency-Key. Server-side deduplication remains the receiver's responsibility.

Supply chain: CI uses least-privilege permissions, deterministic manifests, secret-pattern scanning, and pinned first-party Action commits.

Recovery: the offline outbox preserves work through network loss. Failed delivery does not delete a queued event.

## Residual risk

A stolen unlocked device with its private key is still a serious compromise. A file-backed private key is not a hardware security module, Secure Enclave, TPM, or remote-attested identity.

A hash chain establishes tamper evidence, not factual truth. Provenance establishes history, not correctness.

The epistemic boundary remains:
DECLARED != MEASURED != REPLICATED != EXPLAINED


## Command-authority attacks

The system treats a valid signature as necessary but not sufficient for a high-impact action.

For deployment or rollback, the decision record must survive:
1. signer substitution
2. replay of an old approval
3. payload drift between reviewers
4. role confusion
5. expired approvals
6. single-signer compromise

The security epoch is a local monotonic replay fence. It invalidates all prior authority envelopes when advanced. Dual control requires distinct operator and reviewer keys over the same operation identity and canonical payload.

Break-glass is deliberately not an implicit bypass. It creates an exceptional record with an explicit reason and expiry so the exception itself becomes observable.
