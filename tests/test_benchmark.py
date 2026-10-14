from rqns.audit.benchmark import BenchmarkCase, aggregate, evaluate_outcome
from rqns.audit.consequence_provenance import ConsequenceOutcome, ConsequencePrediction


def test_verified_consequence_scores_only_with_independent_observation():
    case = BenchmarkCase("case-1", "test", "new distinction", "predicted transition fails")
    outcome = ConsequenceOutcome(
        outcome_id="o1",
        parent_outcome_id=None,
        observation="observed",
        falsified=("old-frame",),
        next_tests=("t1",),
        representation_change="frame-A->frame-B",
        independent_observation_ref="external-1",
        status="VERIFIED",
    )
    prediction = ConsequencePrediction("o1", "transition-B", "predicted transition fails", "t1")
    result = evaluate_outcome(case, "synthetic-model", outcome, prediction, 2)
    assert result.surviving is True
    assert result.score >= 5.0


def test_unverified_outcome_cannot_claim_survival():
    case = BenchmarkCase("case-2", "test", "new distinction", "falsifier")
    outcome = ConsequenceOutcome(
        outcome_id="o2",
        parent_outcome_id=None,
        observation="proposed",
        representation_change="frame-A->frame-B",
        status="PROPOSED",
    )
    result = evaluate_outcome(case, "synthetic-model", outcome, None, 4)
    assert result.surviving is False
    assert result.independent_observation_present is False


def test_aggregate_reports_verified_depth_without_ranking_models():
    case = BenchmarkCase("case-3", "test", "new distinction", "falsifier")
    outcome = ConsequenceOutcome(
        outcome_id="o3",
        parent_outcome_id=None,
        observation="observed",
        independent_observation_ref="external-3",
        status="SUPPORTED",
    )
    result = evaluate_outcome(case, "model-a", outcome, None, 3)
    summary = aggregate([result])
    assert summary["cases"] == 1
    assert summary["max_verified_depth"] == 3
