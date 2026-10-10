# EPIE Evidence and Inference Kernel v0.1

## Status

Reference implementation using Python plus the hash-pinned, dependency-free `rfc8785==0.1.4` package for RFC 8785 canonical JSON. Likelihoods and priors are model inputs that require justification; numerical correctness does not validate assumptions.

## Run

    python -m pip install --require-hashes -r requirements-epie.txt

    python -m unittest discover -s tests -p 'test_evez_epie.py' -v
    python -m evez_epie demo

## Core contracts

- Bayesian updates require explicit conditional-independence declarations and unique dependence groups. Repeated groups are rejected; dependent observations must be modeled jointly instead of multiplied as independent evidence.
- Likelihoods must cover the prior hypothesis set and be in [0, 1]. Log weights reduce underflow.
- Expected information gain validates a complete outcome distribution for every hypothesis and returns bits.
- Information gain is computed in bits. `evez_epie.research.expected_value_of_sample_information` separately calculates EVSI: expected best decision utility after observing a test result, minus best decision utility before the test. EVSI prevents a high-entropy test from being mistaken for a useful test when it cannot change a consequential decision.
- `rank_decision_tests` computes EVSI − weighted cost − weighted risk, requiring all terms to use compatible utility units. Tests not explicitly marked permitted are excluded. A positive score never grants authorization.
- `choose_next_test` adds finite-step, affordability, and minimum-net-value stopping conditions so a self-improving loop has a real stop rule.
- Retention score is decision_value × reliability × novelty × exp(−ln(2) × age / half_life). A missing half-life means no age-based decay. This score controls retrieval priority, not truth or permanent retention.
- Identical content hashes can be deduplicated in a hot index, but source references and original artifacts remain preserved.
- Ledger entries use existing EVEZ event names OBSERVED_FACT, EVIDENCE_COMMIT, and CHECKPOINT_ISSUED. This prototype is not yet a wire-compatible adapter for the live event-spine service.
- Ledger hashes use the hash-pinned `rfc8785` package to canonicalize JSON per RFC 8785 before SHA-256. Regression tests exercise the RFC's ECMAScript-compatible IEEE-754 number formatting and UTF-16 property ordering. SHA-256 chaining detects modification relative to the chain but does not authenticate source identity or prove trustworthy time.

## Information reformation with low decay

Treat raw artifacts as a durable evidence layer. Build normalized claims, entity resolution, temporal relations, summaries, and hypothesis receipts as versioned projections. Projections should be recomputable from retained evidence and code/configuration hashes. Never replace source artifacts with lossy summaries.

Separate five layers:

1. Durable evidence: original bytes, metadata, content hash, custody and provenance links.
2. Reformulated knowledge: typed claims and extracted structure linked to exact source spans and extraction version.
3. Active retrieval index: ranked by decision value, reliability, novelty, and domain-specific staleness.
4. Revalidation queue: volatile facts whose half-life elapsed or whose source changed.
5. Contradiction register: preserve incompatible claims side by side until a test resolves them.

Aging lowers priority for stale projections; it does not rewrite history or automatically lower the truth of durable historical claims. For volatile facts, expiration triggers a refresh test, not deletion. Preserve provenance DAGs so compressed/reformulated claims remain traceable to original evidence.

## Acceptance scope

Tests cover posterior normalization, a worked Bayes example, dependency rejection, entropy, information gain, age-decay semantics, index-only deduplication, ledger replay, and tamper detection. Production hardening still requires calibrated likelihoods, authenticated source/custody, a formal event-spine adapter, and application-specific threat modeling.


## Why “reward the search” must be evidence-bound

Do not reward token count, new hypotheses, graph growth, tool calls, or a conclusion merely because it is confident. Those are easy to game and can cause the system to manufacture activity. Reward a search opportunity ex ante only when expected improvement in a downstream decision exceeds its cost and risk. Use EVSI for that decision-focused comparison; keep information gain as a separate diagnostic.

Illustrative two-hypothesis example:

- Prior: P(H1)=0.20, P(H0)=0.80.
- Actions: `act` has utilities +10 if H1 is true and −20 if H0 is true; `defer` has utility 0 either way.
- Before a test, `defer` is optimal (expected utility 0).
- Test A has sensitivity 0.80 and a 0.20 false-positive rate. Its expected information gain is about 0.182 bits, but neither result makes `act` optimal. Its EVSI is 0.
- Test B has sensitivity 0.90 and a 0.05 false-positive rate. On a positive result, P(H1 | +)=0.18/0.22≈0.818. That result changes the optimal action; Test B's EVSI is 1.0 utility unit.
- With cost 0.10 and risk 0.20 in those same utility units, Test B's net expected value is 0.70. Test A's net value is non-positive, so Test B ranks ahead.

These values are synthetic demonstration inputs, not a real-world probability estimate. A production controller must justify/calibrate priors, likelihoods, utilities, and costs; use the same action space before and after the test; and preserve assumptions in the inference receipt.

The operational reward loop should therefore be: propose test → estimate EVSI → subtract declared costs/risk → run only if permitted and above threshold → record raw result → independent verification → compare later held-out predictive performance → update the policy. New text alone receives zero reward. Repeated or derived evidence is not independent reinforcement. If the loop reaches its step budget, evidence budget, authorization boundary, or non-positive marginal value, it stops.
