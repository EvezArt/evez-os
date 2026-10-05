# Federal Pilot Acceptance Matrix

| Control | EVEZ mechanism | Evidence artifact | Pass condition |
|---|---|---|---|
| Provenance | SHA-256 event chain | Event ledger + chain verification | 100% of pilot actions resolve to a predecessor chain |
| Authorization | Fail-closed capability gate | Authorization receipts | Denied action never executes |
| Reproducibility | Pinned code/env + replay | Replay bundle | Same bounded task reproduces expected control result |
| Tamper detection | Chain verification | Corrupted fixture + verifier output | Corruption is rejected |
| Failure honesty | Explicit result status | Success/failure receipt | Failed external action is never recorded as success |
| Human oversight | Review/approval state | Reviewer receipt | Human disposition is traceable |
| Security | Secret scan + least privilege | Scan receipt + SBOM | No secret values in export; dependency manifest present |
| Recovery | Offline outbox + rollback | Recovery receipt | Network loss does not silently discard evidence |
| Epistemic separation | Status taxonomy | Claim ledger | Observation and interpretation remain separate |
| Cost control | Bounded pilot metrics | Cost/performance report | Resource use is measurable |

## Minimum evidence bundle

~~~text
pilot/
  architecture/
  threat-model/
  sbom/
  claims/
  events/
  traces/
  outputs/
  replay/
  tamper/
  authorization/
  rollback/
  independent-rerun/
  limitations/
~~~

Every bundle should include a manifest containing the code revision, environment identifier, generation timestamp, and SHA-256 digest of each artifact.
