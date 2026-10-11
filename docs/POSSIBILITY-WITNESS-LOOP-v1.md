# EVEZ Possibility–Witness Loop v1 — Design Contract

**Purpose:** Make the diagram POSSIBILITY → MEMORY/STATE/FUTURE ↔ HUMAN/MACHINE/WORLD ↔ SYMBOL/OBSERVATION → WITNESS → THE LOOP executable as a testable, bounded, multi-tool workflow.

## 1. Semantics

- **Possibility:** a hypothesis, desired outcome, or candidate action. Never evidence by itself.
- **Memory:** durable, versioned references to prior events, artifacts, accepted decisions, and unresolved issues. Use append-only records where supported; correct mistakes by superseding/retracting, not silent rewrite.
- **State:** a derived snapshot with a parent/checkpoint reference, schema version, timestamp, and hash. State must be reproducible from the declared source when replay is supported.
- **Future:** a forecast or plan with assumptions, uncertainty, acceptance criteria, deadline/expiry, and a test capable of showing the plan failed.
- **Human ↔ Machine:** human intent is not equal to machine interpretation; capability is not authority; authority is not evidence of success.
- **World / Observation:** record the source, collection method, timing, environment, and quality/limitations for every consequential observation.
- **Symbol:** a name, token, equation, label, or model of something. Its referent and measurement method must remain explicit; symbol agreement is not world agreement.
- **Witness:** a factual execution receipt: what was attempted, by whom/which authenticated runtime, under which capability and policy, which inputs/artifacts, what tests actually ran, and what was observed.
- **The Loop:** Observe → Form hypothesis → Plan → Check authority → Execute bounded step → Independently verify → Commit witness → Re-evaluate uncertainty → Continue or stop.

## 2. State classifications

Maintain compatibility with the current EVEZ-OS state vocabulary:
`VERIFIED`, `SUPPORTED`, `INFERRED`, `PROPOSED`, `UNKNOWN`, `STALE`, `CONTRADICTED`, `RETRACTED`.

Meanings:
- `VERIFIED`: acceptance criteria passed with directly linked reproducible evidence and independent review where the risk warrants it.
- `SUPPORTED`: source-backed but not yet fully independently reproduced.
- `INFERRED`: reasoned from listed premises; not directly observed.
- `PROPOSED`: not executed or not yet observed.
- `UNKNOWN`: insufficient evidence, with the smallest resolving test named.
- `STALE`: was supported previously but the relevant inputs/environment may have changed.
- `CONTRADICTED`: conflicting observations are retained with provenance; never flatten the conflict.
- `RETRACTED`: superseded or withdrawn; keep the reason and prior reference.

Do not introduce new application EventType strings into codebases that constrain their event enums. Map this contract to existing types or propose a versioned migration.

## 3. Handoff contract

Every cross-agent handoff must include:
- Protocol and schema version; task ID and correlation ID.
- Issuer and recipient identities that have been authenticated by the transport.
- Intent, constraints, requested capabilities, target/environment, risk level.
- Input artifact references and SHA-256 digests; do not inline credentials.
- Acceptance criteria and falsification tests.
- Issued/expiry timestamps and an idempotency key for retryable operations.
- Approval requirement and current status.
- A terminal result receipt: accepted/rejected/running/succeeded/failed/cancelled/expired, artifact references, observed tests, evidence digest, verifier identity, and remaining uncertainty.

A partial stream, model assertion, manifest entry, or hash without source bytes is not proof of success. Never assume Hermes, OpenClaw, Tailscale, or any remote service is reachable until a harmless authenticated test returns a validated receipt.

## 4. Capability and risk gates

- **R0:** analysis of supplied context.
- **R1:** read-only inventory/status/inspection.
- **R2:** reversible branch-local work or disposable fixtures.
- **R3:** merge, deploy, publish, external messages, spend, account/role/security changes, or production mutations.
- **R4:** unbounded/destructive access, secrets extraction, permission bypass, or uncontrolled data replication is prohibited absent a separately authorized operational process.

Default to read-only and least privilege. Re-check authority immediately before every consequential action. Explicitly confirm the exact target and payload before spending, publishing, merging, changing permissions, rotating credentials, or touching production. A “yes” to overall progress does not authorize each unrelated high-risk action.

## 5. Bounded loop policy

Defaults for the reference implementation:
- At most 3 remediation cycles; each cycle must change a hypothesis or patch and specify a new falsification test.
- At most 3 parallel delegated tasks unless a narrower provider limit applies.
- Explicit step budget, time budget, and output limit for each task.
- Stop on authorization denial, failed verifier without approved recovery, changed artifact hash, expired credentials, cancellation, budget exhaustion, ambiguous write outcome, missing terminal receipt, or absent required artifact.
- On unknown non-idempotent write result: read current state before any retry. Never repeat a successful create/upload.
- If no independent verifier is connected, label self-check separately and cap status at `partially_verified`.

## 6. Witness record

Record a redacted receipt with: task/correlation IDs; schema/runtime/tool versions; authenticated actor and target; capability and policy decision; input and output digests; parent/new state hashes; timestamps; exact tests run (including `not_run` checks); actual output status; immutable artifact locations; verifier method/identity; contradictions; uncertainty; and next resolving test.

Hashes provide integrity checks against the chosen bytes; they do not prove authorship, truth, runtime health, or remote agreement unless backed by authenticated signatures, trusted capture, and independent comparison. Do not place secrets or raw sensitive data in event logs.

## 7. Adapters

Adapters must be truthful about actual capability:
- **GitHub:** begin read-only; use repo and PR references, diffs, statuses, test receipts, then propose branch-local changes.
- **Tailscale:** inspect documented configuration/status and establish an authenticated, harmless connectivity test before claiming nodes are connected. No unverified network-control actions.
- **BioNeMo:** perform host/model/data preflight first. Large downloads, paid compute, data uploads, or scientific runs require explicit resource/scope approval. Preserve seeds, versions, parameters, input/output hashes, and evaluation metrics.
- **Product Design:** state the product/user/goal/constraints; capture supplied screens or actual product evidence before auditing. Distinguish evidence from heuristic opinions.
- **Ads Manager / conversion tools:** report observed account metrics and event configuration read-only. Ad/campaign mutations must follow the owning workflow, require a full exact proposal and approval; live spend requires explicit spend authorization.

An adapter is `specified`, `configured`, `connected`, or `verified` only to the level demonstrated by evidence.

## 8. Acceptance test matrix

1. Invalid schema / extra fields are rejected when the target schema disallows them.
2. Expired, replayed, duplicate, or wrong-recipient handoffs are rejected.
3. Missing capability and denied policy do not execute the tool.
4. A proposal can never satisfy an observation-only acceptance criterion.
5. Hash mismatch invalidates the affected artifact claim.
6. Contradictory evidence remains visible and creates a discriminating test.
7. A failed independent verifier blocks promotion to `verified`.
8. A stream without a terminal receipt remains running/unknown, not succeeded.
9. Read-only mode blocks all state-changing calls at the enforcement point.
10. Retry exhaustion terminates without expanding permissions or scope.
11. Ambiguous non-idempotent writes are reconciled with a read, not repeated blindly.
12. Missing external integration makes that adapter `blocked` or `not_run`, not connected.
13. Advertising spend, permission changes, deploys, and production merges cannot cross the human gate.
14. Every final report lists actual tests run and tests not run.

## 9. Final report schema

Use one overall status: `verified`, `partially_verified`, `blocked`, or `not_run`. Include:
1. Verified facts and sources.
2. Changes/artifacts and exact refs/hashes.
3. Tests actually run and their outputs.
4. Builder report and separate verifier report.
5. Adapter status per service.
6. Contradictions, unknowns, and unresolved risk.
7. Next smallest safe action.

## 10. Non-claims

This contract does not establish consciousness, sentience, autonomous authority, scientific truth, service availability, or successful interoperability. Those require separate, relevant evidence.