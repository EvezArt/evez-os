# Bounded Self-Evolution Cycle 2026-10-07 V2

## Objective

Increase self-steering and reproducibility by making semantic intent selection
explicit, bounded, auditable, and phone-accessible.

## Candidate improvement

Add a deterministic intent optimizer above the existing precision and outcome
contracts.

Inputs:
- explicit candidate intents
- optional evidence strings

Outputs:
- clarity
- specificity
- actionability
- evidence density
- urgency
- reversibility
- semantic complexity
- ambiguity
- risk
- information gap
- deterministic score
- top-two margin

Promotion states:
- REQUIRES_SPECIFICATION
- AMBIGUOUS_TIE
- EVIDENCE_GAP
- OPTIMIZED_CANDIDATE

The optimizer may not invent a hidden user objective.

## Contradiction challenge

Failure modes attacked:

1. A vague candidate must not become authoritative merely because it scores well.
2. A close top-two ranking must remain unresolved.
3. A candidate without sufficient evidence must not become VERIFIED.
4. Risk must reduce the score rather than being rewarded as "decisiveness".
5. Semantic complexity must not be confused with correctness.
6. A mobile operator must expose the same deterministic decision boundary as the
   repository runtime.
7. Licensing discovery must not become presumed ownership or permission.

## Implemented changes

- research/intent_optimizer.py
- research/test_intent_optimizer.py
- mobile/evez_intent.py
- mobile/test_evez_intent.py
- optimizer integrated into research/outcome_engine.py
- optimization telemetry exposed by research/execution_kernel.py
- evezctl optimize-intent
- expanded semantic roles for phenomena, plural role terms, and coined terms
- SPDX declarations on new EVEZ-authored intent files
- .github/workflows/evez-bounded-kernel.yml

## Evidence

Latest branch head at the end of this cycle:

    4dc8f85d5ddfa4b25f30c0e1375b34c81e51bdda

PR #115 remains draft and unmerged.

The base main commit already had failures in the legacy shell/mobile,
wake-up, candidate, defensive, CircleCI verification, and related gates.
Therefore those failures are not attributed to this cycle without differential
evidence.

GitGuardian passed on the preceding head and reported no secrets across 127
commits.

Cubic reported a neutral result because its monthly review allowance was
exhausted.

Debricked reported a neutral result because its scan-credit allowance was
exhausted.

Vercel status checks reported build-rate-limit failures.

## Failed new verification attempt

The newly introduced evez-bounded-kernel workflow was executed and failed.

A second attempt was explicitly rerun to test for flakiness. At the recording
boundary, the rerun was still queued.

The connected GitHub interface exposes the job as failed/queued but does not
return the associated step annotations or job log blob. The container cannot
reach github.com directly. Therefore the exact failing assertion is UNKNOWN.

No claim of verification is made.

## Dissent preserved

D1: The intent scoring weights are engineering heuristics, not a discovered law
of human intention.

D2: Internal reading-complexity output is not a certified Lexile measure.

D3: Commercial pathways are opportunity classes, not revenue forecasts.

D4: Existing repository CI is historically red; current red status cannot be
used as evidence that the new optimizer caused those failures.

D5: The new bounded-kernel gate itself has not yet established a green result.

## Verification boundary

STOP.

Do not merge.
Do not deploy.
Do not alter external billing.
Do not disable failing gates.
Do not reinterpret UNKNOWN as PASS.

Next information-producing operation:

1. obtain the bounded-kernel failing step/annotation from GitHub;
2. reproduce that exact failure locally or in an isolated CI fixture;
3. patch only the evidenced defect;
4. rerun the bounded-kernel gate;
5. promote only after an independent green verification result.
