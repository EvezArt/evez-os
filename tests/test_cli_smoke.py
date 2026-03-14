import subprocess
import sys
import unittest


class TestRootCliSmoke(unittest.TestCase):
    def _run(self, *args):
        proc = subprocess.run(
            [sys.executable, "tools/evez.py", *args],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return proc

    def test_help(self):
        proc = self._run("--help")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("visualize-thought", proc.stdout)

    def test_verify(self):
        proc = self._run("verify")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("verify: PASS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
