import time

from agents.dream.engine import DreamEngine, EmbeddingBackend, Memory
from agents.dream.goal_generator import GoalGenerator
from agents.dream.sharer import DreamSharer
from agents.dream.sleep_cycle import SleepCycleManager


class FakeEmbeddingBackend(EmbeddingBackend):
    def __init__(self):
        pass

    def encode(self, texts):
        mapping = {
            "memory A": [1.0, 0.0],
            "memory B": [0.5, 0.866],  # sim 0.5 with A
            "memory C": [0.0, 1.0],
        }
        out = []
        for t in texts:
            if t in mapping:
                out.append(mapping[t])
            else:
                out.append([0.6, 0.8])
        return out


class DummyEvolutionEngine:
    def __init__(self):
        self.prompts = []

    def create_task_prompt(self, **kwargs):
        self.prompts.append(kwargs)


def test_dream_insight_generation_finds_novel_connections(tmp_path):
    engine = DreamEngine(journal_path=str(tmp_path / "journal.jsonl"), embedding_backend=FakeEmbeddingBackend())
    memories = [
        Memory(memory_id="a", content="memory A", created_at=time.time()),
        Memory(memory_id="b", content="memory B", created_at=time.time()),
        Memory(memory_id="c", content="memory C", created_at=time.time()),
    ]
    result = engine.run_dream_session(memories)
    assert result["session"]["insights_generated"] >= 1
    assert all(i.tags.get("dream_origin") is True for i in result["insights"])
    assert all(i.confidence == 0.6 for i in result["insights"])


def test_goal_generated_when_three_insights_align(tmp_path):
    evo = DummyEvolutionEngine()
    generator = GoalGenerator(goals_path=str(tmp_path / "goals.jsonl"), evolution_engine=evo)
    insights = [
        Memory(memory_id=f"i{i}", content="Need lower memory retrieval latency", created_at=0) for i in range(4)
    ]
    goals = generator.generate_goals(insights, existing_capabilities=[])
    assert len(goals) == 1
    assert goals[0].priority > 0.8
    assert len(evo.prompts) == 1


def test_sleep_cycle_timing_and_phase():
    manager = SleepCycleManager(DreamEngine(embedding_backend=FakeEmbeddingBackend()))
    assert manager.phase_at(0) == "activity"
    assert manager.phase_at(90 * 60 + 1) == "dream"
    assert manager.phase_at((90 + 15) * 60 + 2) == "activity"


def test_dream_sharing_and_absorption_collective_priority():
    sharer = DreamSharer("node-a")
    insight = Memory(memory_id="ins-1", content="Monitor CPU resource usage", created_at=0, embedding=[0.1, 0.9], confidence=0.9)
    msg = sharer.package_top_insights([insight])
    own_memories = [Memory(memory_id="own", content="other", created_at=0, embedding=[0.9, 0.1])]

    collective = []
    for _ in range(3):
        out = sharer.receive(msg, own_memories)
        collective.extend(out["collective"])

    assert out["absorbed"]
    assert any(m.tags.get("priority") == 1.0 for m in collective)
