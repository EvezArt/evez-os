from pathlib import Path
import ast

ROOT = Path(__file__).parents[3]

def test_invariance_has_no_eval_or_exec():
    source = (ROOT / "src/services/invariance.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"eval", "exec"}
        for node in ast.walk(tree)
    )

def test_mesh_health_has_no_shell_true():
    source = (ROOT / "src/services/mesh_health.py").read_text(encoding="utf-8")
    assert "shell=True" not in source

def test_mesh_heal_endpoint_is_local_only():
    source = (ROOT / "src/services/mesh_health.py").read_text(encoding="utf-8")
    assert "heal endpoint is local-only" in source

def test_compose_does_not_ship_openclaw_token_value():
    source = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    expected = "OPENCLAW_TOKEN=${OPENCLAW_TOKEN:?OPENCLAW_TOKEN must be provided via environment}"
    assert expected in source

def test_compose_does_not_ship_telegram_bot_token_value():
    source = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    expected = "TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}"
    assert expected in source

def test_readme_labels_historical_precision_claims():
    source = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Historical precision claims" in source
    assert "CLAIMED != MEASURED != REPLICATED != EXPLAINED" in source
    assert "PROVENANCE != TRUTH" in source