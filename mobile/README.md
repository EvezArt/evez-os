# EVEZ-OS Mobile-First Operator

This directory is the phone-native control plane for EVEZ-OS.

The Galaxy A16 is treated as an operator console, not the production server:

    Galaxy A16 / Termux
            |
            +-- evezctl -> HTTPS gateway / GitHub / remote host
            |
            +-- local evidence + command history
            |
            v
    EVEZ-OS gateway -> services -> append-only event spine

## Design rules

1. The phone should remain useful even when the remote mesh is unavailable.
2. Every remote operation should have a machine-readable result.
3. Secrets stay in $HOME/.config/evez/evez.env, never in Git.
4. The operator shell is idempotent where practical.
5. A command that cannot prove success reports failure instead of pretending it succeeded.

## Install

From a cloned repository:

    bash mobile/install.sh

Then:

    source "$HOME/.config/evez/evez.env"
    evezctl doctor
    evezctl status

## Commands

    evezctl doctor
    evezctl status
    evezctl pipeline
    evezctl spine-event TYPE JSON
    evezctl pull
    evezctl deploy
    evezctl logs

The local witness command creates a SHA-256 chained JSONL record under the mobile operator state directory, so observations can be retained even while the remote mesh is unavailable.

Security controls are exposed through the same operator:

    evezctl security-init
    evezctl security-audit
    evezctl security-manifest
    evezctl authorize DEPLOY '{"commit":"<git-sha>"}'
    evezctl verify-operation ~/.config/evez/device/operations/<operation-id>.json

Device authorization uses a passphrase-protected Ed25519 key. The public key can be registered with the receiving control plane; the private key never belongs in Git.

The offline path adds `queue`, `verify`, `outbox`, and `sync`. Queueing records an event locally first. Sync sends queued events only after the local chain is intact and removes them from the outbox only after a successful 2xx response. `EVEZ_AUTH_TOKEN` may be exported at runtime when the remote endpoint requires bearer authentication; it is never written to the repository.

The command intentionally does not contain credentials or provider-specific deployment tokens. Put only the endpoint and local paths in the generated config file; keep service credentials in the remote runtime or an external secret manager.


### High-impact command authority

For DEPLOY and ROLLBACK, the security policy is dual-control:

    evezctl authority-init operator
    evezctl authority-init reviewer

Both roles sign the same operation ID and canonical payload, then a verifier checks the quorum:

    evezctl authority-sign operator DEPLOY '{"commit":"<sha>"}' <operation-id>
    evezctl authority-sign reviewer DEPLOY '{"commit":"<sha>"}' <operation-id>
    evezctl authority-quorum <operator-file> <reviewer-file> <operator-public> <reviewer-public>

A monotonic security epoch invalidates older approvals:

    evezctl authority-epoch

Break-glass is explicit and time-bounded:

    evezctl break-glass READ_STATUS "operator recovery drill" 5


### Runtime identity

The mobile operator now exposes the executable identity surface:

```bash
evezctl identity
evezctl identity-verify
evezctl self-witness
```

`identity` reports the canonical EVEZ identity, runtime revision, evidence status, and authority boundary.

`identity-verify` verifies the SHA-256 identity contract.

`self-witness` records an `IDENTITY_SELF_WITNESS` event only after both the identity contract and local evidence chain verify.
