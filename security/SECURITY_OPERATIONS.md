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
