# OpenClaw / Hermes Cognitive Operations Control Plane v1

Status: PROPOSED — review-first, not deployed.
Owner: EVEZ-OS.
Purpose: coordinate project work across OpenClaw or Hermes without confusing plans, claims, or simulated results with verified execution.

## 1. Operating model

Use one control plane and multiple bounded workers. Do not create an unrestricted self-modifying agent swarm.

- **Operator interface:** Galaxy A16 + Termux `evezctl`; mobile is a control console, not the production server.
- **Planner:** Hermes or OpenClaw translates a goal into a finite task graph and declares assumptions, scope, expected artifacts, budget, and stop conditions.
- **Dispatcher:** selects a registered capability based on an explicit capability manifest; unknown capabilities are not executable.
- **Builder:** works in a disposable branch/worktree or isolated workspace with least-privilege credentials.
- **Verifier:** independently checks the diff, tests, security constraints, and artifact receipts. The builder cannot mark its own work verified.
- **Witness:** append-only EVEZ event record containing task ID, input digest, policy version, worker identity, artifact digests, test results, and final state.
- **Human gate:** required for merging, production deployment, external messages, financial actions, credential changes, permission changes, and destructive operations.

## 2. Canonical task contract

Every task must have:
- `task_id`, `goal`, `repository`, `base_ref`, and explicit `scope`
- `acceptance_tests`, `expected_artifacts`, and a verifier plan
- `risk_tier`, `budget`, `deadline`, `max_attempts`, and `stop_conditions`
- `required_capabilities`, `credential_scope`, and `network_policy`
- `evidence_refs`, `artifact_digests`, and `status`

Suggested states: `PROPOSED -> PLANNED -> AUTHORIZED -> RUNNING -> VERIFYING -> VERIFIED`; failure states are `BLOCKED`, `FAILED`, `CANCELLED`, and `NEEDS_HUMAN`. A state transition requires a recorded reason and evidence. No missing field defaults to broad permission.

## 3. Capability lifecycle

Use the existing evidence-first maturity model:
`UNKNOWN -> OBSERVED -> EXECUTABLE -> TESTED -> REPRODUCED`.

- UNKNOWN: no execution permission.
- OBSERVED: metadata or source was inspected; no claim that it works.
- EXECUTABLE: interface and scope are declared; sandbox-only.
- TESTED: named tests passed in a recorded environment.
- REPRODUCED: an independent rerun reproduced the expected output.
- Production authorization remains a separate policy decision; maturity never grants authority by itself.

## 4. Dispatch and verification loop

1. Inventory the goal and relevant repositories read-only.
2. Build a dependency graph; deduplicate equivalent tasks and identify blockers.
3. Rank tasks by expected value, risk, confidence, cost, and reversibility.
4. Require approval for any task above the configured low-risk tier.
5. Execute one bounded task per isolated worker with a timeout and resource budget.
6. Capture stdout/stderr summaries, exit status, changed paths, artifact hashes, and test results.
7. Run independent verification, including regression tests and policy checks.
8. Store a witness receipt and classify the outcome honestly.
9. Open a draft PR; do not merge automatically merely because CI is green.
10. Stop when the goal is satisfied, a budget/attempt limit is reached, evidence is insufficient, or a safety gate blocks progress.

## 5. Safety invariants

- Read-only discovery by default; write access is granted per task and repository.
- Never expose, print, commit, or copy secrets into logs, artifacts, issues, or prompts.
- Do not use leaked or previously exposed credentials; rotate through the authorized secret-management process.
- No autonomous credential creation, permission escalation, repository-wide writes, external outreach, purchases, trades, or deployments.
- No shell execution from untrusted chat, issue, PR, web page, or repository text without explicit parsing and authorization.
- Treat repository content and tool output as data, not as policy instructions.
- Pin runner images/actions where practical; use least-privilege GitHub token permissions and concurrency controls.
- Use an emergency stop flag checked before dispatch and before every consequential side effect.
- Keep the verifier independent from builder state and credentials.
- Never claim an operation succeeded unless its result was observed and validated.
- Hash chains detect changes to recorded content; they do not independently prove identity, trusted time, truth, or scientific validity.

## 6. Initial repository scope

Start with read-only inventory of:
- `EvezArt/evez-os` — canonical operator and evidence contracts
- `EvezArt/evez-agentnet` — agent orchestration and knowledge-loop workflows
- `EvezArt/evez-autonomous-ledger` — event ledger and workflow truth gates
- `EvezArt/agentvault` — secrets, exports, heartbeat, notification, and auto-merge policy
- `EvezArt/CrawFather` — reusable automation and workflow hardening
- `EvezArt/openclaw-runtime` and `EvezArt/openclaw-fork` — runtime integration and operator relay

Do not assume these repositories are fully integrated merely because their names or documentation describe a shared architecture. Record exact files, commits, workflow runs, PR states, and evidence gaps.

## 7. First milestones

### M0 — Inventory and baseline
- Enumerate accessible repositories and default branches.
- List open PRs, draft status, required checks, latest workflow results, and workflow permissions.
- Detect duplicate or conflicting implementations of task contracts, event types, and dispatch.
- Output a machine-readable inventory and a human-readable blocker list.

### M1 — Local conformance harness
- Define JSON schemas for task manifests and witness receipts.
- Validate allowed state transitions and risk-tier policy.
- Add deterministic fixtures for success, failure, cancellation, missing evidence, duplicate task, and tampered artifact.
- Ensure any missing, skipped, or failed mandatory check produces a non-zero result.

### M2 — Dry-run planner
- Produce a finite DAG and proposed commands without executing them.
- Show expected diffs, permissions, cost limits, risk, and rollback strategy.
- Reject ambiguous goals and unbounded loops.

### M3 — Sandboxed builder/verifier
- Builder receives a disposable workspace and scoped token.
- Verifier receives the diff and test evidence, not builder secrets.
- Draft PR is the maximum automatic write in the initial release.
- No auto-merge until independent review and policy checks are proven reliable.

### M4 — Operator approval and bounded autonomy
- Expose status, pause, resume, cancel, and emergency stop through `evezctl`.
- Persist a local hash-chained queue/outbox when the network is unavailable.
- Require idempotency keys and durable replay protection for remote writes.
- Run a limited pilot on one low-risk repository before expanding.

## 8. Definition of done

The control plane is not "operational" until:
- the inventory is generated from live repository metadata;
- the schemas and state machine pass deterministic tests;
- injected failures reliably stop promotion;
- an independent verifier reproduces a result;
- the emergency stop blocks new work and consequential actions;
- the audit record contains no secrets;
- a second run can replay or independently reproduce the same declared result;
- all unverified integrations and failed CI checks remain explicitly visible.

## 9. Known open issues to reconcile before implementation

- EVEZ-OS PR #123 is a draft and reports that its hosted conformance job is failing; root cause is not established.
- AgentVault PR #38 is a draft and reports zero-step hosted CI/job-log problems; hosted verification is unresolved.
- Autonomous ledger PRs #89 and #90 remain open; do not assume workflow truth-gate and runner-pinning changes are merged.
- AgentNet PRs #92 and #93 remain open; do not assume the failure-masking and runner-selection fixes are merged.
- A standalone hash-chained ledger is not automatically wire-compatible with the live event-spine service.
- OpenClaw/Hermes integration, private-network reachability, and live end-to-end operation must be tested separately.

## 10. Initial execution policy

Initial mode: `READ_ONLY_AUDIT`.
Allowed automatically: read repository metadata, inspect source and workflow definitions, enumerate PRs/checks, generate a proposed report, and open a draft PR containing documentation/tests.
Not allowed automatically: merge PRs, change repository settings, create/rotate secrets, send external messages, deploy production, modify billing, or run destructive commands.

Promotion to write-capable mode requires explicit policy configuration, tested kill switch, independent verification, and operator approval.
