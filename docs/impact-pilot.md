# One-user impact pilot: verified repository audit

## Purpose

Prove one useful outcome for one person before expanding the architecture: produce a small, reproducible, read-only repository audit that helps its operator decide what to fix next.

This document is a pilot protocol, not a claim that the workflow is already implemented, independently validated, or adopted by an external user.

## Pilot question

Can a developer use the EVEZ mobile-first operator workflow to inspect one repository, receive a prioritized list of evidence-backed findings, and reproduce the checks without granting the agent permission to deploy, merge, alter repository settings, or contact anyone?

## Scope

- Target: one non-critical repository that the operator is authorized to inspect.
- Operator: one user, using the existing Galaxy A16 + Termux workflow where practical.
- Mode: read-only review and local/test execution only.
- Maximum work: one run, one result artifact, one verifier pass.
- Excluded: production deployment, merges, permission changes, credential rotation, external messages, paid services, and autonomous follow-on tasks.

## Procedure

1. Record the repository URL, default branch, commit SHA, date, tool versions, and whether the run is local or remote.
2. Capture a baseline before running checks: existing test status, known issues, and the time the operator spends collecting the same information manually. Mark unknown values as unknown; do not estimate them.
3. Run only checks that are already present and safe for the selected repository. Do not execute untrusted code with secrets available. Do not treat a scanner that exits successfully as proof that the repository is secure.
4. Produce no more than five findings. Each finding must include: severity, affected path or command, observed evidence, why it matters, a reproducible verification step, and confidence/limitations.
5. Have a separate verification pass check that each finding is supported by the captured evidence and that every proposed command is read-only or clearly marked as a suggestion not to execute.
6. Save the report and run metadata as an artifact. If the event-spine tooling is used, record its version and validation result separately. A valid hash chain proves record integrity under the implementation's assumptions, not the truth or completeness of the report.
7. Stop. Do not autonomously create more tasks, change code, merge, deploy, or contact a prospective user.

## Acceptance criteria

The pilot passes only if all of these are true:

- [ ] The exact repository and commit SHA are recorded.
- [ ] Every finding points to observable evidence or is explicitly labeled a hypothesis.
- [ ] A second pass can reproduce the stated checks from the recorded instructions.
- [ ] The report separates confirmed findings, hypotheses, and unknowns.
- [ ] No write, merge, deployment, permission change, or external contact occurred.
- [ ] The artifact records tool versions, commands, exit codes, and failures without exposing secrets.
- [ ] The operator can identify one next action from the report without needing a new architecture or another agent.
- [ ] The operator's time spent and any time saved are measured, not guessed.

Any unchecked item means the pilot is not yet a pass.

## Stop conditions

Stop immediately if the workflow asks for broad credentials, tries to execute an untrusted script with secrets in scope, proposes an irreversible action, produces findings without traceable evidence, exceeds the agreed time/resource budget, or cannot establish which commit was inspected.

On stop: preserve the available logs, mark the run as incomplete, state the blocker, and do not retry automatically.

## Result record

Use this structure for the actual run:

```yaml
pilot_id: evez-repo-audit-001
status: NOT_RUN # PASS | FAIL | BLOCKED | NOT_RUN
repository: ""
commit_sha: ""
run_date_utc: ""
operator_device: "Android + Termux, if used"
tool_versions: {}
baseline:
  manual_minutes: null
  existing_test_status: "unknown"
result:
  findings_count: null
  confirmed_findings: null
  hypotheses: null
  reproducible_checks: null
  secret_exposure_detected: "unknown"
  write_actions_performed: "unknown"
  deployment_or_merge_performed: "unknown"
  operator_minutes: null
  measured_minutes_saved: null
artifact_sha256: ""
limitations: []
next_action: ""
```

Do not change `NOT_RUN` to `PASS` until the evidence exists. Do not enter a time-saved value without a measured baseline and measured run.

## What would count as impact?

For the first pilot, impact means one person receives a more reproducible, evidence-backed decision than they had before, without expanding permissions or creating a new operational risk.

A single successful run proves only that the workflow worked once in that environment. A second independent operator reproducing it is the next validation step. Repeated use, measured time saved, reduced defects, and willingness to use it again are needed before making broader productivity or business claims.

## Pilot report template

- **Outcome:** PASS / FAIL / BLOCKED
- **What changed for the operator:** one concrete sentence
- **Evidence:** artifact path, commit SHA, check outputs
- **Time:** baseline minutes / run minutes / measured difference
- **Risks or false positives:** specific items
- **Next action:** one bounded action, or none
- **External user validation:** NOT DONE until an independent user has reproduced the workflow and confirmed its usefulness
