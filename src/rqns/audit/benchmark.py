"""Model-agnostic benchmark for evidence-bound recursive reasoning.

The benchmark does not score eloquence, confidence, or claims of intelligence.
It scores observable consequence production: prediction, falsification, independent
observation, and the depth at which a tested consequence changes the search space.

It is intentionally runnable with a free-tier model because the model only needs to
return a small structured outcome envelope. Measurement and scoring stay local.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .consequence_provenance import ConsequenceOutcome, ConsequencePrediction


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    prompt: str
    required_distinction: str
    falsifier: str


@dataclass(frozen=True)
class BenchmarkResult:
    case_id: str
    model_id: str
    consequence_depth: int
    prediction_valid: bool
    falsification_present: bool
    independent_observation_present: bool
    representation_change_present: bool
    surviving: bool

    @property
    def score(self) -> float:
        """Transparent diagnostic score, not an intelligence or truth score."""
        components = (
            self.prediction_valid,
            self.falsification_present,
            self.independent_observation_present,
            self.representation_change_present,
            self.surviving,
        )
        return float(sum(components)) + min(self.consequence_depth, 5) * 0.2


def evaluate_outcome(
    case: BenchmarkCase,
    model_id: str,
    outcome: ConsequenceOutcome,
    prediction: ConsequencePrediction | None,
    consequence_depth: int,
) -> BenchmarkResult:
    prediction_valid = bool(
        prediction
        and prediction.source_outcome_id == outcome.outcome_id
        and prediction.predicted_transition
        and prediction.falsifier
        and prediction.test_ref
    )
    independent = bool(outcome.independent_observation_ref)
    representation_change = bool(outcome.representation_change)
    falsification = bool(outcome.falsified) or bool(prediction and prediction.falsifier)
    surviving = outcome.status in {"SUPPORTED", "VERIFIED"} and independent

    return BenchmarkResult(
        case_id=case.case_id,
        model_id=model_id,
        consequence_depth=consequence_depth,
        prediction_valid=prediction_valid,
        falsification_present=falsification,
        independent_observation_present=independent,
        representation_change_present=representation_change,
        surviving=surviving,
    )


def aggregate(results: Iterable[BenchmarkResult]) -> dict[str, object]:
    rows = list(results)
    if not rows:
        return {"cases": 0, "mean_score": 0.0, "max_verified_depth": 0}
    return {
        "cases": len(rows),
        "mean_score": sum(r.score for r in rows) / len(rows),
        "max_verified_depth": max((r.consequence_depth for r in rows if r.surviving), default=0),
        "verified_cases": sum(r.surviving for r in rows),
        "representation_changes": sum(r.representation_change_present for r in rows),
    }
