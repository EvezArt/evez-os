"""Competitive experiment allocation for evolving proposed inventions.

The arena ranks admissible experiments, not the truth of the inventions behind
them. Contradicted proposals are retained as negative knowledge and can seed
future mutation, while evidence remains the only route to epistemic promotion.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .invention import Invention, InventionState
from .optimizer import CandidateTest, TestSelector


@dataclass(frozen=True)
class ExperimentProposal:
    proposal_id: str
    invention_id: str
    test: CandidateTest


@dataclass(frozen=True)
class ArenaDecision:
    selected: str | None
    ranked: tuple[str, ...]
    rejected: dict[str, str]
    heuristic_values: tuple[tuple[str, float], ...]
    rationale: tuple[str, ...]


@dataclass(frozen=True)
class NegativeKnowledge:
    invention_id: str
    reason: str
    failed_falsifier: str | None
    preserved_as: str = "NEGATIVE_KNOWLEDGE"


class EvolutionArena:
    """Apply experimental pressure to a population of proposed inventions."""

    def __init__(self, selector: TestSelector | None = None) -> None:
        self.selector = selector or TestSelector()
        self._negative: list[NegativeKnowledge] = []

    def allocate(
        self,
        proposals: Iterable[ExperimentProposal],
        *,
        max_per_invention: int = 1,
    ) -> ArenaDecision:
        proposals = tuple(proposals)
        grouped: dict[str, list[ExperimentProposal]] = {}
        for proposal in proposals:
            grouped.setdefault(proposal.invention_id, []).append(proposal)

        eligible: list[ExperimentProposal] = []
        rejected: dict[str, str] = {}
        values: dict[str, float] = {}

        for invention_id in sorted(grouped):
            local = sorted(grouped[invention_id], key=lambda p: p.proposal_id)
            selected_count = 0
            for proposal in local:
                if selected_count >= max_per_invention:
                    rejected[proposal.proposal_id] = "invention-budget-exhausted"
                    continue
                result = self.selector.select((proposal.test,))
                if result.selected is None:
                    rejected[proposal.proposal_id] = result.rejected.get(
                        proposal.test.test_id, "not-eligible"
                    )
                    continue
                eligible.append(proposal)
                values[proposal.proposal_id] = proposal.test.heuristic_value()
                selected_count += 1

        ranked_items = sorted(
            eligible,
            key=lambda p: (-values[p.proposal_id], p.proposal_id),
        )
        ranked = tuple(p.proposal_id for p in ranked_items)
        selected = ranked[0] if ranked else None

        return ArenaDecision(
            selected=selected,
            ranked=ranked,
            rejected=rejected,
            heuristic_values=tuple(sorted(values.items())),
            rationale=(
                "Competition is over admissible experiments, not invention truth.",
                "At most the configured experiment budget is allocated per invention.",
                "The heuristic is a planning device; it is not an empirical theorem.",
            ),
        )

    def archive_contradiction(
        self,
        invention: Invention,
        *,
        reason: str,
        failed_falsifier: str | None = None,
    ) -> NegativeKnowledge:
        record = NegativeKnowledge(
            invention_id=invention.invention_id,
            reason=reason,
            failed_falsifier=failed_falsifier,
        )
        self._negative.append(record)
        return record

    def negative_knowledge(self) -> tuple[NegativeKnowledge, ...]:
        return tuple(self._negative)

    def mutation_seeds(self) -> tuple[str, ...]:
        """Return deterministic mutation seeds without inventing observations."""
        return tuple(
            f"mutate:{n.invention_id}:{index}"
            for index, n in enumerate(self._negative)
        )

    @staticmethod
    def eligible_inventions(
        inventions: Iterable[Invention],
    ) -> tuple[Invention, ...]:
        """Keep proposed/testable inventions in the experimental population."""
        allowed = {InventionState.PROPOSED, InventionState.TESTABLE}
        return tuple(
            sorted(
                (item for item in inventions if item.state in allowed),
                key=lambda item: item.invention_id,
            )
        )
