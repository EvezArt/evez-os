from evez_evidence_runtime.dependencies import DependencyGraph
from evez_evidence_runtime.federation import WitnessFederation
from evez_evidence_runtime.witness import witness

def test_dependency_blast_radius():
    graph = DependencyGraph()
    graph.depends_on("claim-a", "evidence-x")
    graph.depends_on("claim-b", "claim-a")
    assert graph.blast_radius("evidence-x") == {"claim-a", "claim-b"}
    assert graph.epistemic_debt({"evidence-x"})["claim-b"] == 1

def test_federation_keeps_contradiction_visible():
    a = witness("github", "repo", "2026-09-30T00:00:00-07:00", {"status": "ready"}, independence_group="provider:github")
    b = witness("vercel", "deployment", "2026-09-30T00:01:00-07:00", {"status": "failed"}, independence_group="provider:vercel")
    record = WitnessFederation().compare(a, b)
    assert record.relation == "CONTRADICTS"
