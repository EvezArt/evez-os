# DESA-S Integration Map

DESA-S is the runtime adaptation layer joining the existing EVEZ evidence format and EVEX exchange protocol.

## One system

OBSERVATIONS -> ENTITY ECC -> DOMAIN INDUCTION -> SME PROFILE -> SELF-WITNESSING TARGETER -> ADAPTIVE SOCRATIC QUESTION -> DESA-S STATE

DESA-S STATE splits into two portable artifacts:

- EVEZ records the evidence-bearing adaptation state.
- EVEX carries the accountable state transition.

## Artifact roles

EVEZ records evidence-bearing state.

DESA-S constructs and revises a bounded temporary domain, competence profile, question policy, entity-error model, and witness target.

EVEX carries the accountable state transition describing the DESA-S change.

The layers remain separate:

- EVEZ identity and integrity do not prove truth.
- DESA-S inference does not create authority.
- EVEX authorization fields do not activate themselves.
- A selection receipt records the targeting decision; it does not prove that the selected target was optimal.
- A correction proposal is not a verified entity identity.
- An SME profile is demonstrated-competence state, not a credential.

## Interoperability contract

A DESA-S transition uses the existing EVEX state.transition object with an explicit adaptation extension:

    adaptation.profile = desas-s.v1
    adaptation.domain_state_hash = hash(domain state)
    adaptation.sme_profile_hash = hash(SME state)
    adaptation.selection_receipt_hash = receipt integrity
    adaptation.question_id = selected question
    adaptation.target_id = selected witness target

A DESA-S-aware runtime can validate those hashes and replay the bounded controller. A runtime that does not implement DESA-S can still consume ordinary EVEX because the extension is explicit.

## CLI

After installation:

    evez-socratious
    evez-socratious --evex
    evez-socratious --evex --compact

The commands run a deterministic opaque-domain fixture. They do not call an external model, network endpoint, or credential.

## Verification ladder

The repository validates:

1. deterministic runtime serialization;
2. entity error-syndrome handling;
3. targeter self-inclusion;
4. rejected-target preservation;
5. EVEX adaptation binding;
6. no implicit epistemic promotion;
7. EVEZ-to-EVEX portability boundaries;
8. GitHub Actions execution of the benchmark.

This remains a protocol and controller benchmark. It is not a universal domain-learning benchmark and does not establish consciousness or general intelligence.

## Research boundary

The strongest falsifiable question is whether explicit domain induction, bounded SME modeling, adaptive questioning, semantic entity error correction, and self-witness targeting reduce silent error and unsupported certainty compared with answer-only orchestration on held-out domains.
