import ast
from pathlib import Path

def test_invariance_service_does_not_execute_python_expressions():
    path = Path(__file__).parents[3] / "src" / "services" / "invariance.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    forbidden = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
            forbidden.append(node.func.id)
    assert forbidden == []

def test_invariance_service_has_explicit_ast_interpreter():
    path = Path(__file__).parents[3] / "src" / "services" / "invariance.py"
    source = path.read_text(encoding="utf-8")
    assert "ast.parse(expression, mode=\"eval\")" in source
    assert "only dict.get is allowed" in source
