# EVEZ-OS Mobile-First Operator

This directory is the phone-native control plane for EVEZ-OS.

The Galaxy A16 is treated as an operator console, not the production server:

    Galaxy A16 / Termux
            |
            +-- evezctl -> HTTPS gateway / GitHub / remote host
            |
            +-- local evidence + command history
            +-- multimodal signal adapters
            +-- bounded outcome kernel
            +-- precision gate
            +-- semantic mapper
            +-- rights audit
            |
            v
    EVEZ-OS gateway -> services -> append-only event spine

## Design rules

1. The phone should remain useful even when the remote mesh is unavailable.
2. Every remote operation should have a machine-readable result.
3. Secrets stay in $HOME/.config/evez/evez.env, never in Git.
4. The operator shell is idempotent where practical.
5. A command that cannot prove success reports failure instead of pretending it succeeded.
6. Adapter discovery never creates consent.
7. Planning never creates consequential authorization.
8. Vague intent never silently becomes an executable interpretation.
9. Missing licensing never becomes assumed permission.

## Install

From a cloned repository:

    bash mobile/install.sh

Then:

    source "$HOME/.config/evez/evez.env"
    evezctl doctor
    evezctl status

## Core commands

    evezctl doctor
    evezctl status
    evezctl pipeline
    evezctl spine-event TYPE JSON
    evezctl pull
    evezctl deploy
    evezctl logs

The local witness command creates a SHA-256 chained JSONL record under the
mobile operator state directory, so observations can be retained even while
the remote mesh is unavailable.

## Precision gate

Before vague language becomes an executable plan:

    evezctl precision --intent "do everything fully"

This must reject unbounded wording.

A complete specification can be checked as JSON:

    evezctl precision --spec SPEC.json

The required contract identifies subject, action, scope, inputs, constraints,
evidence, acceptance criteria, time, and authority.

The rule is:

    UNKNOWN > invented interpretation

## Semantic and complexity mapping

Map arbitrary text, words, phrases, concepts, and coined terms:

    evezctl lexile --text "interoopticological inferenciology"

or:

    evezctl lexile --file prompt.txt

The mapper returns deterministic token and n-gram atoms, abstraction density,
syllable estimates, information proxy bits, semantic role classes, coined-term
recognition, and an internal complexity proxy.

It deliberately reports:

    INTERNAL_PROXY_NOT_CERTIFIED_LEXILE

It does not reproduce MetaMetrics proprietary scoring or treat the result as a
certified Lexile measure.

## Rights and licensing audit

Audit the repository's declared rights and commercial opportunity classes:

    evezctl rights-audit

The audit distinguishes:

    DECLARED
    UNDECLARED
    LICENSE_DOCUMENT

and produces candidate pathways such as hosted service, support, enterprise
integration, training, publication, media licensing, and commercial licensing
of newly created rights.

It never turns an undeclared asset into presumed permission.

## Information frontier

    evezctl frontier PACKET

The frontier planner selects the next bounded information operation while
preserving UNKNOWN, contradiction, incomplete-source, and expected-information-
gain semantics.

## Multimodal reachability

Discover actual local adapters:

    evezctl signal-capabilities --consent-scope operator-info \
      --consent-scope operator-alerts \
      --output ~/.config/evez/signal-capabilities.json

The detector probes installed Termux commands. It does not infer consent.

Dry-run a negotiated signal:

    evezctl signal SIGNAL.json --auto \
      --capabilities ~/.config/evez/signal-capabilities.json

Actual delivery is explicit:

    evezctl signal SIGNAL.json --auto \
      --capabilities ~/.config/evez/signal-capabilities.json --deliver

Supported local delivery adapters include stdout text, Android notifications,
Termux TTS, and Termux vibration. Failed adapters produce receipts and proceed
through the negotiated fallback order before failing closed.

## Bounded outcome kernel

Prepare finite resources:

    evezctl kernel "build the missing capability" \
      --budget budget.json \
      --requests requests.json \
      --channels ~/.config/evez/signal-capabilities.json

The kernel compiles the intent, applies the precision gate, allocates finite
resources, prepares an operator signal, and exposes whether the operation is
ready for verification or requires authorization.

A vague intent stops with REQUIRES_SPECIFICATION.

Consequential operations remain blocked without authorization.

## Security controls

    evezctl security-init
    evezctl security-audit
    evezctl security-manifest

Device authorization uses a passphrase-protected Ed25519 key. The public key
can be registered with the receiving control plane; the private key never
belongs in Git.

The offline path adds queue, verify, outbox, and sync. Queueing records an event
locally first. Sync sends queued events only after the local chain is intact and
removes them from the outbox only after a successful 2xx response.
EVEZ_AUTH_TOKEN may be exported at runtime when the remote endpoint requires
bearer authentication; it is never written to the repository.

## High-impact command authority

For DEPLOY and ROLLBACK, the security policy is dual-control:

    evezctl authority-init operator
    evezctl authority-init reviewer

Both roles sign the same operation ID and canonical payload, then a verifier
checks the quorum.

A monotonic security epoch invalidates older approvals.

Break-glass is explicit and time-bounded.

## Runtime identity

    evezctl identity
    evezctl identity-verify
    evezctl self-witness

identity reports the canonical EVEZ identity, runtime revision, evidence status,
and authority boundary.

identity-verify verifies the SHA-256 identity contract.

self-witness records an IDENTITY_SELF_WITNESS event only after both the identity
contract and local evidence chain verify.
