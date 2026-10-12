# EVEZ Federated Plugin Mesh v1 — Architecture RFC

**Status:** DESIGN / NOT DEPLOYED  
**Owner:** EVEZ  
**Tracking:** https://github.com/EvezArt/evez-os/issues/127

## Goal

Allow distinct EVEZ operator plugins and approved connected services to request each other's capabilities via a common broker while each service retains its own identity, credentials, policies, and revocation controls.

The mesh brokers explicit service contracts. It does not automatically give one ChatGPT plugin the right or technical ability to call another plugin's private internal tools. Cross-provider services must publish a documented, authenticated interface that the broker can reach.

## Components

1. **Operator clients:** evez-tools, evez-project-operator, evezart-cognysynaptic-operator, evezart-operator, plus explicitly configured external adapters.
2. **Service manifests:** versioned JSON documents containing service ID, owner, version, manifest digest, transport, endpoint reference, input/output JSON Schema, declared capabilities, data classification, quotas, timeout, idempotency policy, health state, and revocation handle. Do not place credentials in manifests.
3. **Directory:** stores manifests and health observations. Discovery is public only to authenticated callers and never grants invocation rights.
4. **Authorization broker:** evaluates an explicit grant tuple: `(caller identity, target service ID, exact capability, data scope, expiry, risk tier)`. Default deny. Every grant has an issuer, creation time, expiry, and revocation procedure.
5. **Adapter runtime:** makes a single bounded request to an approved HTTPS/MCP/service endpoint after the broker approves it. Adapter identity is distinct from the end-user identity and is least-privileged.
6. **Policy/approval service:** handles elevated approvals with exact request binding. No self-approval or capability self-grant. Policy outage means deny.
7. **Audit/evidence writer:** records redacted metadata, hashes, decisions, test evidence and correlation IDs. It does not record credentials or raw sensitive payloads.
8. **Workflow composer:** allows a finite DAG of tool calls under caller-controlled budgets, cancellation, retry rules and a read-only kill switch.

## Trust boundaries

- ChatGPT permission to use an app is a host-level permission; it does not create a plugin-to-plugin runtime API.
- A manifest declaration describes what a service offers; it does not authorize a caller.
- Provider OAuth/API credentials remain in their provider or secret-manager boundary. Never copy one plugin's credential into another plugin's environment.
- All service responses are untrusted data, not instructions. Validate output schemas and cap response sizes.
- Live connectivity, identity, authorization, application health and successful actions are separate acceptance checks.
- SHA-256/JCS values prove byte consistency relative to a trusted expected digest, not truth, ownership or authorship.

## Initial data contract

Example manifest (non-operational placeholder):

```json
{
  "schema_version": "evez.service-manifest.v1",
  "service_id": "example.readonly-search",
  "owner": "evez",
  "version": "1.0.0",
  "manifest_sha256": "<computed-at-publication>",
  "transport": {
    "kind": "https-json",
    "endpoint_ref": "secret-manager://evez/services/search/endpoint"
  },
  "capabilities": ["search.read"],
  "input_schema": {
    "type": "object",
    "properties": {"query": {"type": "string", "maxLength": 500}},
    "required": ["query"],
    "additionalProperties": false
  },
  "output_schema": {
    "type": "object",
    "properties": {"items": {"type": "array", "maxItems": 20}},
    "required": ["items"],
    "additionalProperties": false
  },
  "limits": {
    "timeout_seconds": 10,
    "max_request_bytes": 16384,
    "max_response_bytes": 131072,
    "requests_per_minute": 30
  },
  "risk_tier": "R0_READ_ONLY"
}
```

The endpoint reference is illustrative only. It is not a live credential or proof of an available service.

## Authorization and invocation

Before each call the broker MUST:
1. Authenticate the caller and resolve a stable service identity.
2. Resolve the exact target service ID, pinned version and manifest digest.
3. Verify an unexpired grant matching caller, service, exact capability and data scope.
4. Validate strict input schema; reject unknown fields.
5. Check read-only mode, rate/fan-out/depth budgets, time limit and cancellation.
6. For elevated actions, require an externally produced approval bound to actor, correlation/request ID, target tool/version, capability, manifest digest and parameter digest. Deny on any mismatch or policy outage.
7. Verify target endpoint against exact allowlist and enforce network-level egress policy; no redirects; do not permit local/loopback/link-local/private destinations except specifically authorized private service ranges.
8. Execute once under a timeout; validate response schema and byte limits.
9. Apply idempotency-key conflict checks, log redacted audit metadata and return result plus correlation ID and provenance.
10. On timeout, audit failure, unknown result, policy failure or circuit-breaker trip, stop the affected workflow. Do not blindly retry writes.

Suggested risk tiers:
- **R0_READ_ONLY:** bounded lookups and analysis with minimized data.
- **R1_REVERSIBLE:** idempotent, reversible test changes in a sandbox.
- **R2_HIGH_IMPACT:** code writes, repo changes, deployments, messages or permission changes; requires bound approval.
- **R3_IRREVERSIBLE_OR_PUBLIC:** deletion, production releases, payments, public publishing or credential changes; supervised approval and rollback/compensation plan required.

## Workflow-composition limits

Initial defaults for a local/mock run:
- maximum 8 nodes per DAG;
- maximum fan-out 3 from a node;
- maximum dependency depth 4;
- maximum 1 retry for transient read-only calls only;
- maximum total wall time 120 seconds;
- maximum 1 MiB response per node and 4 MiB total response;
- cancellation checked between every node;
- maximum 3 remediation cycles;
- one builder pass and one verifier pass; verifier may veto and cannot edit its own policy or approve the builder.
- `READONLY=1` by default; a kill switch must work independently of the agent workflow.

These are proposal defaults and must be confirmed by resource/load tests before live use.

## Builder/verifier and release contract

Builder submits a minimal diff and change envelope. Verifier must inspect the diff independently and run both positive and negative tests. When a distinct agent/context is unavailable, call it a self-check, not independent verification. No auto-merge or production deploy is part of the initial release.

Required tests include missing/invalid identity, missing capability, disabled target, expired grant, manifest/version mismatch, unexpected input/output fields, denied target host, redirect, oversized request/response, timeouts, policy outage, approval binding mismatch, read-only switch, idempotency conflict, audit sink failure, cancellation, exhausted budget, circuit breaker, replay mismatch and self-grant/self-approval prevention.

## Mobile-first / Termux smoke plan

1. Run unit tests locally with mock adapters only.
2. Validate every manifest against the schema and compute RFC 8785 JCS SHA-256.
3. Start the broker bound to loopback and with read-only mode enabled.
4. Register two mock services on loopback only through a dedicated test configuration; never weaken production endpoint policy for the tests.
5. Exercise one read-only DAG: mock discovery → mock lookup → verifier schema check.
6. Exercise negative cases: caller missing, ungranted capability, policy unavailable, timeout and kill-switch.
7. Export a redacted evidence capsule with commit, command, exit status, test names, digests and NOT RUN live checks.
8. Do not expose a port, create a public tunnel, change provider permissions, or run real mutations from the smoke test.

## Rollback and stop

Stop on test failure, unexpected diff, policy denial/outage, credential concern, audit sink failure, external target mismatch, user cancellation or budget exhaustion. Preserve redacted diagnostics, disable the affected manifest, and restore the prior reviewed revision. Deployment, external publication and permission changes are separate release gates.

## Acceptance evidence status

- **SOURCE-VERIFIED:** current private evez-tools v1.3.0 manifest and source include capability grants, a local registry, HTTPS allowlists, read-only default, JCS digests, bounded HTTP requests, idempotency and an external high-risk approval hook.
- **OBSERVED:** a GitHub connector can read/write this repository; EvezArt account has admin/push access.
- **NOT VERIFIED:** a running EVEZ broker endpoint, shared live service credentials, cross-plugin direct invocation, live Hermes policy adapter, independent agent runtime, or production deployment.
- **NOT RUN:** all implementation and live integration tests in this RFC.
