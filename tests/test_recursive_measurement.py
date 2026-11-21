from rqns.audit import (
    CausalType,
    Discrepancy,
    EvidenceState,
    RecursiveAuditor,
    Residual,
)


def test_generation_chain_preserves_parent_hash():
    auditor = RecursiveAuditor()
    first = auditor.add_generation(
        generation="G0",
        intention="append-only history",
        artifact="EventSpine",
        execution="append(event)",
        observation="event recorded",
        source_refs=["src/rqns/core/interfaces.py"],
    )
    second = auditor.add_generation(
        generation="G1",
        intention="durable history",
        artifact="EventSpine",
        execution="restart process",
        observation="persistence not tested",
        source_refs=["src/rqns/core/interfaces.py"],
    )

    assert second.parent_generation == "G0"
    assert second.parent_hash == first.content_hash()
    assert auditor.verify_chain()


def test_unknown_is_not_promoted_without_observation():
    assert (
        RecursiveAuditor.claim_state(
            has_observation=False,
            has_source=True,
            has_reproducible_transform=True,
        )
        == EvidenceState.UNKNOWN
    )


def test_supported_requires_observation_and_source():
    assert (
        RecursiveAuditor.claim_state(
            has_observation=True,
            has_source=True,
            has_reproducible_transform=False,
        )
        == EvidenceState.SUPPORTED
    )


def test_contradiction_survives_missing_reproducibility():
    discrepancy = Discrepancy(
        between=("intention", "artifact"),
        causal_type=CausalType.INTENTION_ARTIFACT,
        statement="declared immutable history differs from observed storage",
        evidence_refs=("E-001",),
        state=EvidenceState.CONTRADICTED,
    )
    residual = Residual(
        residual_id="RES-001",
        observation="events live in process memory",
        expectation="historical state survives restart",
        question="does the event history persist across process termination?",
        candidate_variable="PERSISTENCE_INTEGRITY",
        evidence_refs=("E-001",),
    )
    auditor = RecursiveAuditor()
    auditor.add_generation(
        generation="G1",
        intention="immutable historical record",
        artifact="in-memory EventSpine",
        execution="append",
        observation="event exists in memory",
        source_refs=["E-001"],
        discrepancies=[discrepancy],
        residuals=[residual],
    )

    assert auditor.latest.discrepancies[0].state == EvidenceState.CONTRADICTED
    assert auditor.latest.residuals[0].state == EvidenceState.UNKNOWN


def test_audit_seal_detects_last_record_tampering():
    auditor = RecursiveAuditor()
    auditor.add_generation(
        generation="G0",
        intention="record evidence",
        artifact="audit trace",
        execution="append",
        observation="record exists",
        source_refs=["E-002"],
    )
    seal = auditor.seal()
    assert auditor.verify_seal(seal)

    auditor.generations[0].observation = "rewritten after sealing"
    assert not auditor.verify_seal(seal)


def test_sealed_auditor_rejects_append():
    auditor = RecursiveAuditor()
    auditor.add_generation(
        generation="G0",
        intention="record evidence",
        artifact="audit trace",
        execution="append",
        observation="record exists",
        source_refs=["E-003"],
    )
    auditor.seal()

    try:
        auditor.add_generation(
            generation="G1",
            intention="continue",
            artifact="audit trace",
            execution="append",
            observation="new record",
            source_refs=["E-004"],
        )
    except RuntimeError:
        return
    raise AssertionError("sealed auditor accepted a new generation")
