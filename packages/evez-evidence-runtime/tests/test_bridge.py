from evez_evidence_runtime.integration_bridge import EvidenceBridge

def test_bridge_preserves_sources_and_records_relation():
    bridge = EvidenceBridge()
    a = bridge.ingest(
        source="github",
        observation_type="commit",
        observed_at="2026-09-30T00:00:00-07:00",
        payload={"state": "committed"},
        independence_group="provider:github",
    )
    b = bridge.ingest(
        source="vercel",
        observation_type="deployment",
        observed_at="2026-09-30T00:01:00-07:00",
        payload={"state": "committed"},
        independence_group="provider:vercel",
    )
    assert bridge.sources() == ("github", "vercel")
    assert bridge.compare(a, b).relation == "CORROBORATES"
    assert len(bridge.export()) == 2
