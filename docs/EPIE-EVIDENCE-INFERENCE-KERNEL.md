# EPIE Evidence and Inference Kernel v0.1

## Status

Reference implementation using the Python standard library. Likelihoods and priors are model inputs that require justification; numerical correctness does not validate assumptions.

## Run

    python -m unittest discover -s tests -p 'test_evez_epie.py' -v
    python -m evez_epie demo

## Core contracts

- Bayesian updates require explicit conditional-independence declarations and unique dependence groups. Repeated groups are rejected; dependent observations must be modeled jointly instead of multiplied as independent evidence.
- Likelihoods must cover the prior hypothesis set and be in (0, 1]. Log weights reduce underflow.
- Expected information gain validates a complete outcome distribution for every hypothesis and returns bits.
- Test utility is value × information_gain_bits − weighted cost − weighted risk. These are dimensionless scores until an application calibrates them. Tests not explicitly marked permitted are excluded.
- Retention score is decision_value × reliability × novelty × exp(−ln(2) × age / half_life). A missing half-life means no age-based decay. This score controls retrieval priority, not truth or permanent retention.
- Identical content hashes can be deduplicated in a hot index, but source references and original artifacts remain preserved.
- Ledger entries use existing EVEZ event names OBSERVED_FACT, EVIDENCE_COMMIT, and CHECKPOINT_ISSUED. This prototype is not yet a wire-compatible adapter for the live event-spine service.
- Ledger hashes use an RFC 8785-style canonical JSON serializer for the supported JSON subset before SHA-256 hashing. Inputs outside that interoperable subset (including unsafe integers and unpaired surrogates) are rejected. SHA-256 chaining detects mutation relative to the chain but does not authenticate source identity or prove trustworthy time.

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
