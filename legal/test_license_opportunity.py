import tempfile
from pathlib import Path

from legal.license_opportunity import audit

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "MIT.py").write_text("# MIT License\nprint('owned')\n", encoding="utf-8")
    (root / "unknown.py").write_text("print('review me')\n", encoding="utf-8")
    (root / "third_party.md").write_text("License: CC-BY-NC-4.0\n", encoding="utf-8")

    result = audit(root)

    by_path = {row["path"]: row for row in result["findings"]}
    assert by_path["MIT.py"]["status"] == "DECLARED"
    assert by_path["unknown.py"]["status"] == "UNDECLARED"
    assert by_path["unknown.py"]["legal_review"] is True
    assert by_path["third_party.md"]["legal_review"] is True
    assert result["summary"]["legal_review"] >= 2
    assert len(result["audit_sha256"]) == 64

print("license opportunity tests: PASS")
