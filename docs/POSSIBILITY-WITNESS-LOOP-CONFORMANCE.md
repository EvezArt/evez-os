# EVEZ Possibility–Witness Loop: executable conformance harness

## Run locally (Python standard library only)

From the repository root, run these three commands:

    python -m py_compile evez_possibility_witness_loop.py scripts/run_possibility_witness_conformance.py
    python -m unittest discover -s tests -p 'test_possibility_witness_loop.py' -v
    python scripts/run_possibility_witness_conformance.py --output possibility-witness-report.json

A successful fixture runner exits 0 and writes a JSON witness report. Its result_status reports the bounded fixture checks; verification_status deliberately remains partially_verified because the report generator is not an independent verifier.

## Covered by the unit suite

- Strict top-level fields, timestamp parsing, expiry, and future-dated handoffs.
- Recipient mismatch, missing capabilities, and read-only write denial.
- R3 approval-flag enforcement and R4 denial.
- Local duplicate idempotency-key detection.
- Exact artifact SHA-256 comparison and tamper detection.
- Proposal/inference cannot satisfy a VERIFIED acceptance criterion.
- Missing terminal receipts and failed/missing checks cannot be promoted to verified.
- Lack of an independent verifier caps a successful receipt at partially_verified.
- Contradictory observations retain both records and require a resolution test.
- Hash-sealed witness mutation detection and bounded remediation cycles.

## Scope limits

The replay guard in this harness is intentionally in-memory and process-local, for deterministic conformance testing. Production replay prevention must use durable, atomic storage with expiry/retention and concurrency handling. The harness does not authenticate network identities, execute tool calls, prove external service connectivity, or authorize production actions. The test receipt is evidence of these local checks only.

The workflow archives logs and a report where the CI artifact service is available and also publishes diagnostic output in the GitHub job summary. Full-repository CI, live integrations, and independent external verification remain separate checks.
