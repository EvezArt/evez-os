# EVEZ Recovery Alternative Matrix

A runtime failure does not authorize the next action. Evidence about the failure constrains the admissible action set.

## Pipeline

`FAILURE → CLASSIFY → GENERATE → SAFETY/AUTHORITY GATES → BUDGET → DOMINANCE PRUNING → SELECT → EXECUTE ELSEWHERE → OBSERVE → VERIFY / NEXT / CAIN / QUARANTINE`

## Alternative classes

| Failure class | Candidate alternatives | Required guard |
|---|---|---|
| TRANSIENT | bounded retry, backoff, half-open probe | idempotency or compensation |
| PERSISTENT | circuit break, fallback, defer | dependency evidence |
| CAPACITY | backpressure, queue, bulkhead, degrade | bounded load |
| DEPENDENCY | alternate provider, cached result, defer | semantic contract |
| AUTHORIZATION | deny, request human review, quarantine | authority proof |
| INTEGRITY | quarantine, reconcile, restore known-good | preserve evidence |
| CONFIGURATION | validate, isolate, revert known-good | provenance |
| DEPLOYMENT | rollback, canary halt, replay | receipt + health evidence |
| PROVENANCE | stop promotion, source reconciliation | source evidence |
| ADVERSARIAL | isolate, reject, preserve witness | no external mutation |
| UNKNOWN | gather discriminating evidence | no invented classification |

## Operational unlocks

1. **Failure is not an action selector.** A timeout does not imply retry; retryability depends on idempotency, budget, dependency health, and expected information.
2. **Compensation is semantic undo, not deletion.** Distributed recovery commonly requires compensating transactions, and these must tolerate retries. citeturn0search1turn0search8
3. **Irreversible work is a pivot.** Once an irreversible step has occurred, the system must move into completion/reconciliation rather than pretending rollback can erase the event. citeturn0search8turn0search2
4. **Outbox/idempotency close common delivery gaps.** For cross-service workflows, durable event publication and idempotent consumers reduce duplicate/lost-transition failure modes. citeturn0search2
5. **Circuit breakers and bulkheads contain repeated dependency failure.** They are complements to, not substitutes for, evidence and recovery policy. citeturn0search4turn0academia12

## Epistemic boundary

- FAILURE means the expected operation did not succeed as observed.
- UNKNOWN means evidence is insufficient to establish success or failure.
- CONTRADICTION means relevant observations disagree.
- A recovery receipt proves that a recovery decision was recorded. It does not prove the underlying system recovered.


## Recovery ladder

A failed recovery attempt is retained as evidence and excluded from immediate reselection. The coordinator can advance to the next admissible alternative without silently resetting the failure history:

`ATTEMPT → OBSERVE → NEXT_ALTERNATIVE → FILTER(ALREADY_ATTEMPTED) → SELECT`

This creates bounded fallback depth rather than an unbounded retry storm. A later candidate is not interpreted as proof that the prior candidate was safe, correct, or successful.
