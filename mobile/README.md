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

The command intentionally does not contain credentials or provider-specific deployment tokens. Put only the endpoint and local paths in the generated config file; keep service credentials in the remote runtime or an external secret manager.
