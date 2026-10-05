# Mobile Security Operations Contract

The mobile operator is treated as an untrusted endpoint. Access is evaluated per resource and operation rather than inferred from network placement.

## Fail-closed rules

- Unknown actions are denied.
- Missing device identity is denied for signed operations.
- Invalid signatures are denied.
- Broken evidence chains are denied.
- Dirty working trees block deployment.
- Missing second-factor approval blocks deployment.
- Failed remote delivery never deletes the local outbox item.
- Repository secret-pattern findings fail CI.
- CI receives read-only repository contents permission.

## Bootstrap

    python mobile/evez_guard.py init-device

Authorize a deployment:

    export EVEZ_SECOND_FACTOR=1
    python mobile/evez_guard.py authorize DEPLOY '{"commit":"<git-sha>"}'

Verify it:

    python mobile/evez_guard.py verify-operation ~/.config/evez/device/operations/<operation-id>.json

Never commit the private key.

## Supply chain

Dependencies and Actions are inputs to the trust boundary. Prefer pinned immutable references and explicit provenance over floating tags.


## Command authority

High-impact actions use dual control. The two approvals must:
- refer to the same operation ID
- contain the same action
- contain byte-equivalent canonical payloads
- use distinct operator and reviewer roles
- use the current security epoch
- remain unexpired
- verify against the expected public-key fingerprints

Bootstrap separate roles:

    evezctl authority-init operator
    evezctl authority-init reviewer

Create two approvals for one operation identity:

    evezctl authority-sign operator DEPLOY '{"commit":"<git-sha>"}' <operation-id>
    evezctl authority-sign reviewer DEPLOY '{"commit":"<git-sha>"}' <operation-id>

Then verify the quorum:

    evezctl authority-quorum <operator-file> <reviewer-file> <operator-public> <reviewer-public>

Advancing the security epoch invalidates older operation envelopes:

    evezctl authority-epoch

### Break-glass

Break-glass is exceptional, bounded, and recorded:

    evezctl break-glass READ_STATUS "operator recovery drill" 5

It is not an invisible bypass. The record includes the reason, actor, issue time, expiry, and security epoch.
