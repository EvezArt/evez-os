# Fleet Integrity Policy

This repository is the control-plane policy reference for EVEZ GitHub automation.

## Invariants

1. Standard GitHub-hosted runners only unless a repository explicitly documents an intentional exception.
2. `runs-on` must not resolve through an uncontrolled administrator variable such as `RUNNER_LABEL`.
3. A failed operation must remain observable as FAILED. Do not use `continue-on-error` or shell failure swallowing to manufacture success.
4. External effects use explicit states: `NONE`, `REQUESTED`, `CONFIRMED`, `FAILED`, `UNKNOWN`.
5. A repository README, prompt, configuration, or local simulation establishes DECLARED/OBSERVED state only. It does not establish LIVE external state.
6. Every deployment claim should be backed by a reproducible receipt containing target, commit, workflow/run identifier, timestamp, result, and artifact hash where applicable.
7. Missing external credentials or services are recorded as UNKNOWN/UNAVAILABLE, not silently simulated.

## Zero-billing baseline

The default runner is `ubuntu-latest`. Paid/larger GitHub-hosted runner labels are prohibited by the fleet guard unless an explicit exception is recorded.

The policy is intentionally narrow: it does not claim that every external service is free. It prevents the GitHub workflow layer from selecting a larger runner merely because a mutable repository variable says to do so.

## Evidence rule

A green workflow proves only the checks actually executed by that workflow. It does not prove deployment, revenue, external API availability, or real-world effects unless those effects are independently observed and recorded.
