# GitHub Verification Evidence Ingestion

This module normalizes a saved GitHub Actions API snapshot into a deterministic evidence report. It does not make API requests, retry workflows, merge PRs, or promote code.

## Bundle format

Save the GitHub Actions run record and its job records together. Preserve the actual API responses rather than manually retyping conclusions. A bundle has `candidate_commit`, `run`, and `jobs` fields. `run` is the workflow-run API object; `jobs` is the array of job objects returned by the workflow-jobs endpoint.

## Termux / CLI

```bash
evezctl verification-ingest github-actions-bundle.json --output verification-report.json
```

Or run directly:

```bash
python mobile/github_verification_ingest.py github-actions-bundle.json --output verification-report.json
python mobile/test_github_verification_ingest.py
```

## State meanings

- `FAILED`: a named test/verification step explicitly failed.
- `VERIFIER_UNAVAILABLE`: at least three jobs show the same zero-step/no-start failure signature.
- `VERIFIER_INCONCLUSIVE`: source commit mismatch, no job records, setup failure without test evidence, or incomplete execution.
- `EXECUTED_UNVERIFIED`: a test step succeeded, but independent review is not established.

This adapter intentionally never emits `VERIFIED` and always sets `promotion_eligible=false`. GitHub reporting a successful run is not the same thing as independent verification, and this parser has no authority to promote or deploy.

Every report preserves SHA-256 digests of the source bundle, run record, job record, and step records. These digests make later mutation detectable when the original bundle is retained; they do not authenticate who supplied the bundle.
