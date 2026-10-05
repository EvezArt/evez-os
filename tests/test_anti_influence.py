from src.recursive.anti_influence import (
    BlindPanel,
    CapabilityFirewall,
    CapabilityGrant,
    EpistemicState,
    EvidenceEnvelope,
    InfluenceAssessment,
    InfluenceEdge,
    InfluenceGraph,
    InfluenceSignals,
    MemoryQuarantine,
    MemoryState,
    SealedObservation,
    assess_influence,
)


def _evidence(evidence_id: str, source_id: str, influence_score: float = 0.1):
    return EvidenceEnvelope(
        evidence_id=evidence_id,
        source_id=source_id,
        observer_id=f"observer-{evidence_id}",
        compartment_id="compartment-a",
        content="immutable observation",
        channel="web",
        influence=InfluenceAssessment(influence_score, "LOW", ()),
    )


def test_extreme_pressure_triggers_high_influence_and_quarantine():
    assessment = assess_influence(
        InfluenceSignals(urgency=1.0, secrecy=1.0)
    )
    assert assessment.level == "HIGH"
    assert assessment.quarantine_recommended


def test_memory_quarantine_requires_independent_witness():
    quarantine = MemoryQuarantine()
    decision = quarantine.decide(
        [_evidence("e1", "source-a"), _evidence("e2", "source-b")],
        witnessed=False,
        independent_sources=2,
        contradiction_free=True,
        state=EpistemicState.SUPPORTED,
    )
    assert decision.state is MemoryState.QUARANTINED


def test_memory_quarantine_admits_clean_supported_evidence():
    quarantine = MemoryQuarantine()
    decision = quarantine.decide(
        [_evidence("e1", "source-a"), _evidence("e2", "source-b")],
        witnessed=True,
        independent_sources=2,
        contradiction_free=True,
        state=EpistemicState.SUPPORTED,
    )
    assert decision.state is MemoryState.ADMISSIBLE
    assert len(decision.evidence_hashes) == 2


def test_blind_panel_refuses_early_fusion():
    panel = BlindPanel(["A", "B", "C"])
    panel.submit(SealedObservation("round-1", "A", "comp-a", "H1"))
    panel.submit(SealedObservation("round-1", "B", "comp-b", "H2"))

    try:
        panel.fuse("round-1")
    except RuntimeError:
        pass
    else:
        raise AssertionError("blind panel fused before every observer submitted")


def test_blind_panel_only_fuses_after_all_observers_submit():
    panel = BlindPanel(["A", "B", "C"])
    for observer_id in ("A", "B", "C"):
        panel.submit(
            SealedObservation(
                "round-1",
                observer_id,
                "compartment",
                "H1" if observer_id != "B" else "H2",
            )
        )

    result = panel.fuse("round-1")
    assert result.majority == "H1"
    assert result.disagreement > 0
    assert result.ready_for_interpretation


def test_capability_firewall_rejects_untrusted_issuer():
    firewall = CapabilityFirewall(["WITNESS"])

    try:
        firewall.grant(
            CapabilityGrant(
                "agent-a",
                "external:browser",
                "TARGET",
                "untrusted content cannot grant authority",
            )
        )
    except PermissionError:
        pass
    else:
        raise AssertionError("untrusted issuer granted a capability")


def test_capability_firewall_requires_explicit_trusted_grant():
    firewall = CapabilityFirewall(["WITNESS"])
    firewall.grant(
        CapabilityGrant(
            "agent-a",
            "external:browser",
            "WITNESS",
            "explicit test grant",
        )
    )

    decision = firewall.authorize(
        subject="agent-a",
        capability="external:browser",
        requested_by="agent-a",
    )
    assert decision.allowed


def test_influence_graph_backtracks_only_observed_edges():
    graph = InfluenceGraph()
    graph.add(
        InfluenceEdge(
            "target",
            "agent",
            "authority",
            "e1",
            True,
        )
    )
    graph.add(
        InfluenceEdge(
            "agent",
            "conclusion",
            "prompt",
            "e2",
            False,
        )
    )

    result = graph.backtrack("target")
    assert ("target", "agent") in result.paths
    assert all("conclusion" not in path for path in result.paths)


def test_evidence_provenance_hash_is_stable():
    evidence = _evidence("e1", "source-a")
    assert evidence.content_hash == evidence.content_hash
    assert len(evidence.provenance_hash) == 64
