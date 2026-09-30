from evez_evidence_runtime.evolution import EvolutionArena, ExperimentProposal
from evez_evidence_runtime.invention import Invention, InventionState
from evez_evidence_runtime.optimizer import CandidateTest


def test_arena_competes_on_experiments_not_truth():
    arena = EvolutionArena()
    proposals = [
        ExperimentProposal(
            "p-a", "i-a",
            CandidateTest("t-a", "a", 10, 2, 1, 2, .1, True, True, True, True,
                          dependency_unlock=2, reversibility=1),
        ),
        ExperimentProposal(
            "p-b", "i-b",
            CandidateTest("t-b", "b", 5, 4, 1, 1, .1, True, True, True, True,
                          dependency_unlock=1, reversibility=1),
        ),
    ]
    result = arena.allocate(proposals)
    assert result.selected == "p-b"
    assert result.rationale[0].startswith("Competition is over")


def test_arena_limits_one_action_per_invention():
    arena = EvolutionArena()

    def make_test(ident):
        return CandidateTest(ident, ident, 1, 1, 1, 1, 0, True, True, True, True)

    result = arena.allocate((
        ExperimentProposal("a", "same", make_test("a")),
        ExperimentProposal("b", "same", make_test("b")),
    ))
    assert result.selected == "a"
    assert result.rejected["b"] == "invention-budget-exhausted"


def test_contradiction_becomes_negative_knowledge():
    arena = EvolutionArena()
    invention = Invention(
        "i1", (), ("repo",), ("t1",), (), (), ("f1",), ("receipt",),
        InventionState.PROPOSED,
    )
    record = arena.archive_contradiction(
        invention, reason="observed output contradicted prediction", failed_falsifier="f1"
    )
    assert record.preserved_as == "NEGATIVE_KNOWLEDGE"
    assert arena.mutation_seeds() == ("mutate:i1:0",)


def test_eligible_population_excludes_archived_and_contradicted():
    proposed = Invention("a", (), (), ("t",), (), (), (), ())
    archived = Invention("b", (), (), ("t",), (), (), (), (), InventionState.ARCHIVED)
    contradicted = Invention("c", (), (), ("t",), (), (), (), (), InventionState.CONTRADICTED)
    result = EvolutionArena.eligible_inventions((archived, contradicted, proposed))
    assert [item.invention_id for item in result] == ["a"]
