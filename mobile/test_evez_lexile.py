import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
result = subprocess.run(
    [
        sys.executable,
        str(root / "mobile" / "evez_lexile.py"),
        "--text",
        "interoopticological inferenciology classifies truth taxonimists",
    ],
    capture_output=True,
    text=True,
    check=True,
)
packet = json.loads(result.stdout)
assert packet["measure_type"] == "INTERNAL_PROXY_NOT_CERTIFIED_LEXILE"
assert "interoopticological inferenciology" in packet["coined_terms_present"]
assert "truth taxonimists" in packet["coined_terms_present"]
assert len(packet["mapping_sha256"]) == 64

print("mobile lexile-semantic tests: PASS")
