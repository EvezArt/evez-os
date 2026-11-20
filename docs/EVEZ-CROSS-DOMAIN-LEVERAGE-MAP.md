# EVEZ Cross-Domain Leverage Map

**Status:** source-inspected portfolio synthesis; not a deployment or runtime certification.  
**Baseline:** `EvezArt/evez-os` main at `ef7c8e6c25ebca0d315b12932b6496edc615a984`.

## Executive finding

The portfolio's highest-leverage asset is not a particular model or agent. It is the recurring pattern across existing modules: structured inputs, deterministic transformations, provenance, explicit uncertainty, and verification gates. The bottleneck is **evidence continuity across boundaries**: a research result can be hashed, a civic record can cite source hashes, a mobile event can be hash-chained, and an agent handoff can be versioned—but those artifacts do not yet share one demonstrated terminal receipt that reliably connects question → source → transformation → action → independent verification.

This is an architectural inference from inspected source, not a claim that all components run together.

## Evidence map

| Capability | Inspected artifacts | Concrete capability | Boundary |
|---|---|---|---|
| Mobile-first operations | `mobile/evezctl`, `mobile/evez_state.py` | Termux CLI, local evidence spine, outbox, chain verification, sync path | Device execution and live endpoint reachability not tested here |
| Claim discipline | `research/epistemic_evaluator.py` | Epistemic states, provenance checks, evidence hash checks, contradiction input | Structural validity does not establish real-world truth |
| Information prioritization | `research/information_frontier.py` | Deterministic operation ranking by uncertainty, impact, novelty, freshness, disagreement, and cost | Ranking depends on honest inputs and a bounded source inventory |
| Portable artifacts | `evidence/evidence_capsule.py` | Artifact manifest, SHA-256 digests, capsule verification | Integrity is not authorship, truth, or completeness |
| Civic accountability | `civic/arsenal_ledger.py`, `civic/civic_fusion.py` | Provenance-preserving normalization, record hashes, derived investigation leads | A lead is not evidence of misconduct; entity matching can be wrong |
| Agent coordination | `EvezArt/evez-agentnet` README | Eight named roles: SPINE, TRUNK, DEPLOY, VAULT, HARVEST, SCOUT, WITNESS, CAIN | README documents intent; executable runtime needs direct tests |
| Message transport | `EvezArt/evez-mesh/server.py`, `broker.py`, bridge MVP spec | Health/topology endpoints and bounded handoff contract | Inspected broker advertises pub/sub routes that are not implemented; status reports in-memory backend |
| Operating policy | `docs/LORD-GOD-EVEZ-PEARL-CHARTER.md` | PEARL loop, R0–R4 gates, explicit connectivity states, stop conditions | Policy becomes enforcement only when code and CI reject violations |

## Unifying design: Evidence Continuity Layer

Give every meaningful output one stable **Evidence ID** and a portable receipt with:

- `schema_version`, `evidence_id`, UTC `created_at`, `domain`, `producer`, and `method`
- `input_refs[]` and `output_refs[]`, each carrying a locator, media type, byte length, and SHA-256 when bytes exist
- `claim_status` using the receiving system's supported epistemic states; never silently promote `UNKNOWN` to `SUPPORTED`
- `expected`, `observed`, `result`, and `limitations`
- `verification`: verifier identity/type, checks actually run, PASS/FAIL/NOT RUN, and evidence
- `risk_class`, scoped `authorization_ref` if applicable, `correlation_id`, and terminal status
- `receipt_sha256` over canonicalized receipt content with the digest field omitted

Do not add new event enums to an event-sourced subsystem without migration. The receipt is a transport artifact, not a replacement for repository-defined events. Existing sorted-key JSON is deterministic for current code, but is not automatically a full RFC 8785 implementation.

## Five-domain flywheel

1. **Research:** the information frontier selects a bounded next question and explains its expected value.
2. **Evidence:** source material is captured in a capsule; claim evaluation preserves unknowns and contradictions.
3. **Synthesis:** domain adapters derive a report or graph while retaining links to original record hashes.
4. **Execution:** the operator turns one accepted result into a bounded task envelope with capabilities, expiry, and stop conditions.
5. **Verification:** a separate verifier checks acceptance criteria; the terminal receipt points to inputs, code version, tests, and output digests.

Feedback returns to research only when the verifier identifies a specific, testable uncertainty. Otherwise the cycle stops. This is bounded learning, not infinite self-modification.

## Prioritized build frontier

Scores are ordinal planning judgments, not measured telemetry.

| Priority | Work item | Impact / reuse / cost (1–5) | Definition of done |
|---|---|---|---|
| P0 | Shared evidence receipt contract | 5 / 5 / 2 | Schema, canonical digest rules, positive and negative fixtures |
| P0 | Adversarial verifier fixtures | 5 / 5 / 2 | Tampering, missing provenance, stale references, and invalid status transitions fail closed |
| P1 | Capsule + claim-evaluator adapter | 5 / 4 / 3 | One CLI command emits a receipt both tools can independently validate |
| P1 | Mobile integration | 4 / 5 / 3 | Termux records receipt digest to existing local spine; offline path works |
| P1 | Mesh adapter | 5 / 4 / 4 | Local fixture transfer passes auth, idempotency, recipient binding, and terminal acknowledgement |
| P2 | Civic/scientific adapters | 4 / 4 / 3 | Derived reports preserve sources and distinguish leads from established facts |
| P2 | Portfolio status board | 3 / 4 / 3 | Statuses are source-backed: specified, configured, connected, verified, blocked, or not run |

## Adversarial acceptance gates

1. Change one artifact byte: receipt verification must fail.
2. Remove provenance from a supported claim: fail or explicitly downgrade to unresolved.
3. Mirror one source across multiple URLs: do not count mirrors as independent corroboration.
4. Put hostile instructions inside an artifact: treat them as data, never policy.
5. Replay a task ID with a different payload: reject it.
6. Request a consequential operation without scoped authorization: deny before execution.
7. Make transport unavailable: report BLOCKED, never CONNECTED or VERIFIED.
8. Skip tests or lose the verifier: report NOT RUN, never green.
9. Produce a civic co-occurrence lead: label it a lead, not an accusation.
10. Interrupt mobile sync: preserve the local chain and retry without duplicating terminal results.

## Strategic consequence

- **Model-centric → evidence-centric:** workers can be swapped without losing provenance.
- **Repo islands → interoperable modules:** domain schemas remain local; a small versioned receipt crosses boundaries.
- **Confidence theater → falsification:** completion depends on observable tests and explicit failure behavior.
- **Phone as limitation → phone as control plane:** the Galaxy A16/Termux workflow can originate tasks and preserve evidence offline without requiring every computation on-device.
- **Autonomy as slogan → bounded authority:** each worker gets a narrow task, finite budget, verifier, and stop condition.

## First experiment

Use only two local synthetic fixtures: one research result and one civic record. Create receipts, verify independently, mutate one byte, and confirm rejection; then record the final test receipt in the existing local EVEZ spine. No live-account changes, external messages, production credentials, deployments, or real-person allegations are needed.

**Stop condition:** if any receipt survives tampering, provenance loss, or unauthorized status promotion, halt integration and repair the contract before connecting more domains.

## Evidence limits

This map is based on source files inspected in the named repositories. It does not certify live services, external APIs, deployments, runtime interoperability, current CI results, or scientific validity. The next implementation should be a small branch-local schema and fixture test suite, followed by independent review.
