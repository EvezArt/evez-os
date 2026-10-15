# EPIE Sequential Research Controller

## Purpose

The controller makes a research loop earn additional compute budget only from new, precommitted, independently verified held-out improvement. It prevents one evaluation cohort from being reused for multiple adaptive search trials in the same budget, spends a finite family-wise error budget across successive trial looks, and caps both per-trial and lifetime research credits.

It uses the existing CHECKPOINT_ISSUED event type with a namespaced payload; it does not introduce new event type strings.

## Run the test suite

    python -m pip install --require-hashes -r requirements-epie.txt
    python -m unittest discover -s tests -p 'test_evez_epie_controller.py' -v

## Minimal API

    from evez_epie import JsonlLedgerStore, ResearchExperimentController

    controller = ResearchExperimentController(
        JsonlLedgerStore("state/epie-ledger.jsonl"),
        budget_id="casework-budget-v1",
        initial_budget=20.0,
        max_total_credit=5.0,
        max_credit_per_trial=0.5,
        family_alpha=0.05,
        credit_rate=1.0,
        min_cases=100,
    )

Before running a research test, call reserve with a stable trial ID, a fresh set of independent evaluation-unit IDs, and the baseline/candidate forecasts. Do not include observed outcomes. The reservation records hashes for both the cohort identity and the exact forecast bundle, assigns the next alpha-spending slot, and debits search plus risk cost from the finite budget.

After those outcomes become available, call settle with those same forecast records, the observed outcomes, and the required verification gates. Settlement rejects changed forecasts or reused cohort identities, verifies the declared gates, computes a conservative one-sided Hoeffding lower confidence bound on paired held-out negative-Brier-score improvement, and issues credit only if the lower bound is positive and the capped credit exceeds the trial's costs.

A retry with the same trial ID and identical inputs is idempotent. Reusing a trial ID with altered inputs fails. Reusing the same cohort for a different trial fails. Abandoned reservations keep their costs debited and their alpha slot consumed.

## CLI

Install the project or run from the repository with Python. The budget policy is required on every command so a caller cannot silently reset it by omitting policy fields.

    python -m evez_epie research-status \
      --ledger state/epie-research.jsonl --budget-id research-v1 \
      --initial-budget 20 --max-total-credit 5 --max-credit-per-trial 0.5 \
      --family-alpha 0.05 --credit-rate 1 --min-cases 100

    python -m evez_epie research-reserve \
      --ledger state/epie-research.jsonl --budget-id research-v1 \
      --initial-budget 20 --max-total-credit 5 --max-credit-per-trial 0.5 \
      --family-alpha 0.05 --credit-rate 1 --min-cases 100 \
      --trial-id trial-0001 --records-json frozen-forecasts.json \
      --search-cost 0.25 --risk-cost 0.05

    python -m evez_epie research-settle \
      --ledger state/epie-research.jsonl --budget-id research-v1 \
      --initial-budget 20 --max-total-credit 5 --max-credit-per-trial 0.5 \
      --family-alpha 0.05 --credit-rate 1 --min-cases 100 \
      --trial-id trial-0001 --samples-json settled-holdout.json

The first research-status/reserve/settle call opens the budget policy receipt if the ledger is empty. Thereafter, policy changes are rejected. A single controller ledger is dedicated to one budget ID; another budget requires a separately authorized ledger path. The initial-budget and credit caps should come from a trusted operator policy, not from an autonomous search agent.

## The bounds

Trial number t receives:

    alpha_t = family_alpha / (t * (t + 1))

Because the sum over t = 1..infinity of 1/(t(t+1)) is 1, total allocated alpha does not exceed family_alpha. This protects against unadjusted repeated looks when the per-trial confidence bounds and evidence assumptions are valid. It does not repair dependent cases or false provenance.

Credits are bounded by the smallest of the positive lower confidence bound, the per-trial cap, and the remaining lifetime pool. credit_rate is restricted to [0, 1], so credits cannot multiply themselves into a larger budget. Maximum spendable budget is bounded by initial_budget + max_total_credit. If costs exceed the available budget, reserve returns STOP and does not register a trial.

## Epistemic and security limits

- The caller-supplied independence and verification flags are not proofs. An independent verifier must audit provenance and evaluation-unit independence.
- The reservation commits forecast hashes before outcomes are passed to settle, but a caller that already knows the outcomes could still lie about timing. Stronger guarantees require a sealed evaluation service, trusted timestamping, or an independent custodian.
- Unique IDs only prevent accidental or same-ledger reuse when IDs are stable. The holdout identity should be derived from a durable evaluation manifest, not generated afresh to evade deduplication.
- The Brier-score bound is conservative and assumes independent evaluation units within the cohort. Clustering requires cluster-level scoring or a dependence-aware interval.
- Credits are internal utility units, not money. Calibrate cost/risk/score units before allowing credits to authorize external actions.
- The controller's file lock coordinates controller instances using the same local ledger path on POSIX systems. The ledger hash chain detects mutation; it does not authenticate original source identity or protect against a compromised host.

The intended reward is not "more tool calls". It is a finite, auditable research budget that is replenished only by new evidence that improves a frozen prediction on a fresh, verified holdout, after risk and cost.
