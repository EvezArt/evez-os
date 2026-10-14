from evez_evidence_runtime.optimizer import CandidateTest, TestSelector
from evez_evidence_runtime.dependencies import DependencyGraph

def test_optimizer_rejects_unsafe_and_non_observable():
    selector = TestSelector()
    result = selector.select([
        CandidateTest("unsafe", "unsafe", 10, 10, 1, 1, 0, True, True, False, True),
        CandidateTest("blind", "blind", 10, 10, 1, 1, 0, True, False, True, True),
    ])
    assert result.selected is None
    assert result.saturation == "SATURATED"
    assert result.rejected["unsafe"] == "unsafe"
    assert result.rejected["blind"] == "no-observable"

def test_optimizer_removes_dominated_test():
    selector = TestSelector()
    result = selector.select([
        CandidateTest("strong", "strong", 10, 5, 1, 2, .1, True, True, True, True),
        CandidateTest("weak", "weak", 5, 1, 1, 2, .1, True, True, True, True),
    ])
    assert result.selected == "strong"
    assert result.rejected["weak"] == "dominated"

def test_optimizer_finds_epistemic_bottleneck():
    graph = DependencyGraph()
    graph.depends_on("claim", "assumption")
    graph.depends_on("model", "claim")
    result = TestSelector().select(
        [CandidateTest("probe", "probe", 4, 2, 1, 1, .1, True, True, True, True)],
        graph=graph,
        uncertain={"assumption"},
    )
    assert "claim" in result.bottlenecks
    assert result.selected == "probe"

def test_unknown_is_not_verified():
    from evez_evidence_runtime.optimizer import claim_state_transition
    assert claim_state_transition("UNKNOWN").value == "UNKNOWN"
    assert claim_state_transition("PASS").value == "SUPPORTED"
