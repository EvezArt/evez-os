# EVEZ Energy Witness (prototype)

A first software slice for recording attestable exported-energy evidence. This is **not** a live utility integration, certified metering system, currency, or token issuer.

## Operator rewards

Operators earn nothing for uptime, CPU cycles, self-reported generation, or merely submitting readings. A future reward policy may allocate a disclosed, prefunded pool only after independent utility settlement confirms net exported energy. Settlement must be unique, final, and attributable to a registered meter and operator. Corrections must be new ledger events, never silent edits.

## Prototype features

- Registry-bound meter and operator identity
- Calibration validity and timezone-aware interval checks
- Non-overlapping intervals and monotonic cumulative Wh register
- Signed-reading check (HMAC solely for local tests)
- Duplicate-reading rejection and SHA-256 chained JSONL records
- Explicit reward status: NOT_ISSUED_PENDING_INDEPENDENT_SETTLEMENT

## Production gaps

HMAC is unsuitable as a public meter identity scheme because every holder of the shared secret can forge readings. Replace it with vendor/utility-verifiable public-key signatures, secure meter provisioning, calibration traceability, and utility settlement APIs or signed settlement files. A hash chain proves record continuity, not physical truth. Independent audits and reconciliation are mandatory.

## Tests

From repository root run: python -m unittest discover -s energy_witness/tests -v

Never commit meter credentials, wallet keys, private keys, or customer data.
