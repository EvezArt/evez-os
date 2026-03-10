import subprocess
import sys
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestCliSmoke(unittest.TestCase):
    def run_cmd(self, *args):
        return subprocess.run(
            [sys.executable, *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def test_evez_help(self):
        result = self.run_cmd("tools/evez.py", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage", result.stdout.lower())

    def test_evez_verify(self):
        result = self.run_cmd("tools/evez.py", "verify")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("verify", result.stdout.lower())

    def test_run_all_help(self):
        result = self.run_cmd("tools/run_all.py", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("seed", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
