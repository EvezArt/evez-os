import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from self_mutation_engine import SelfMutationEngine



def test_analyze_module_extracts_functions(tmp_path: Path):
    module = tmp_path / "sample.py"
    module.write_text(
        """

def alpha(x):
    return x + 1


def beta(a, b):
    if a > b:
        return a - b
    return b - a
""".strip()
        + "\n",
        encoding="utf-8",
    )
    engine = SelfMutationEngine(repo_root=tmp_path)
    functions = engine.analyze_module("sample.py")
    assert [f.name for f in functions] == ["alpha", "beta"]
    assert functions[1].complexity_signals >= 1


def test_mutate_builds_pr_payload(tmp_path: Path):
    module = tmp_path / "mod.py"
    module.write_text(
        """

def score(n):
    total = 0
    for i in range(n):
        total += i
    return total
""".strip()
        + "\n",
        encoding="utf-8",
    )
    engine = SelfMutationEngine(repo_root=tmp_path)
    out = engine.mutate({"mod.py": 0.1}, threshold=0.5)

    assert out["underperformers"] == ["mod.py"]
    assert out["pull_request"]["title"].startswith("chore(self-mutation)")
    assert out["proposals"]
    assert out["proposals"][0]["file_path"] == "mod.py"