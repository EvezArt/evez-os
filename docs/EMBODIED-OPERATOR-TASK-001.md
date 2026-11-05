# EVEZ Embodied Agent Operator: Task 001

**Status:** PROPOSED; device execution not yet evidenced  
**Target:** `EvezArt/evez-os`, mobile-first operator  
**Mode:** supervised, non-destructive smoke test  
**Budget:** one run, maximum three review rounds; no unattended loop

## Objective

Prove the smallest useful end-to-end operator path on the actual Android/Termux device: local prerequisites are present, the local witness chain verifies, and one harmless test witness can be recorded and verified. This tests the evidence path before attempting broader agent work.

## Ground truth

- **SOURCE-OBSERVED:** The repository's `mobile/README.md` documents `evezctl doctor`, `evezctl status`, local witness storage, and verification.
- **SOURCE-OBSERVED:** `mobile/evezctl` defines `doctor`, `witness TYPE JSON`, and `verify`. The `doctor` path checks dependencies, expected files, and the local chain. The `status` path makes a gateway health request and verifies the local chain.
- **UNKNOWN:** Whether the current Galaxy A16 Termux installation has the required dependencies, a current checkout, a valid local chain, or working network access. No live device execution is available from this documentation task.
- **UNKNOWN:** Whether the remote gateway is healthy now. Repository documentation is not live service telemetry.

## Operator procedure

Run from the cloned repository in Termux. Do not paste tokens, environment files, private keys, or raw secrets into the evidence packet.

1. Confirm the checkout and inspect changes:
   ```bash
   git status --short --branch
   git rev-parse --short HEAD
   ```
2. Run the local preflight:
   ```bash
   evezctl doctor
   ```
   If it fails, stop and capture only the redacted error summary. Do not work around missing files by creating empty placeholders.
3. Verify the existing local evidence chain:
   ```bash
   evezctl verify
   ```
4. Record one clearly labeled, non-sensitive test event:
   ```bash
   evezctl witness OPERATOR_SMOKE_TEST '{"task":"embodied-operator-task-001","purpose":"local-chain-verification"}'
   ```
5. Verify again:
   ```bash
   evezctl verify
   ```
6. Optionally run `evezctl status` only if a remote GET request is acceptable and connectivity is available. It is not required to pass the local evidence test. Do not run `pipeline`, `spine-event`, `sync`, `pull`, or `deploy` as part of this task.

## Acceptance criteria

- [ ] The repository revision and working-tree status are recorded.
- [ ] `evezctl doctor` completes successfully, or its failure is preserved as a blocker.
- [ ] Pre-test `evezctl verify` succeeds.
- [ ] The test witness command returns success and does not contain secrets.
- [ ] Post-test `evezctl verify` succeeds.
- [ ] The evidence packet labels every result as observed, user-reported, unknown, or hypothesis.
- [ ] No remote write, deployment, merge, permission change, credential change, purchase, or external contact occurs.

**Pass predicate:** all required local checks succeed and the post-test chain verifies. A failed precondition is **BLOCKED**, not a pass. A successful local hash-chain check proves integrity against the verifier's expected chain; it does not by itself prove that event contents are factually true or independently authored.

## Builder / verifier contract

**Builder:** follow the procedure, collect command exit codes and minimal redacted output, and propose one targeted repair if a check fails.

**Verifier veto:** reject claims without command output or equivalent direct evidence; reject secret-bearing logs; reject changes to the acceptance criteria; reject any attempt to expand into network writes or deployment. If only the same operator/model reviews the result, label it `SELF_CHECK`, not independent verification.

## Stop conditions

Stop immediately on a secret appearing in output, unexpected repository changes, a broken chain, an authorization prompt for a consequential operation, uncertain command behavior, or a failed acceptance criterion. Do not retry more than once after one targeted, reversible correction. Stop after three rounds or when the acceptance predicate passes.

## Evidence record template

Copy this template into the task report after running the procedure:

- Run ID:
- Timestamp and timezone:
- Repository URL / commit:
- Working tree:
- `doctor`: PASS / FAIL / NOT RUN; exit code:
- Pre-test `verify`: PASS / FAIL / NOT RUN; exit code:
- Test witness: PASS / FAIL / NOT RUN; event type only:
- Post-test `verify`: PASS / FAIL / NOT RUN; exit code:
- Optional `status`: PASS / FAIL / NOT RUN; remote health result:
- Redactions performed:
- Verifier: INDEPENDENT / SELF_CHECK / NOT RUN:
- Decision: ACCEPT / REVISE / BLOCK / STOP
- Residual risks and next action:

Do not attach full environment files, bearer tokens, private keys, personal notifications, or unrelated logs.

## Change scope

This task adds documentation only. It does not change runtime behavior, event schemas, permissions, CI, deployment, or service configuration.
