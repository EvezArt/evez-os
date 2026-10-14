import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from pathlib import Path
import tempfile

from research.spacetime_dashboard import create_handler


class SpacetimeDashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        ledger = Path(self.temp.name) / "empty.jsonl"
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(ledger))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.thread.join, 2)
        self.addCleanup(self.server.shutdown)
        self.base = "http://127.0.0.1:%d" % self.server.server_port

    def get_json(self, path):
        try:
            with urlopen(self.base + path, timeout=3) as response:
                return json.loads(response.read().decode("utf-8")), response.status, response.headers
        except HTTPError as exc:
            with exc:
                body = json.loads(exc.read().decode("utf-8"))
                return body, exc.code, exc.headers

    def test_health_discloses_readonly_loopback_scope(self):
        body, status, headers = self.get_json("/api/health")
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(body["mode"], "read-only")
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_interval_endpoint(self):
        body, status, _ = self.get_json("/api/interval?dt=1e-9&dx=1")
        self.assertEqual(status, 200)
        self.assertEqual(body["classification"], "SPACELIKE")

    def test_profile_endpoint_returns_diagnostics_only(self):
        body, status, _ = self.get_json("/api/profile?radius=10&sigma=1&samples=101")
        self.assertEqual(status, 200)
        self.assertIn("diagnostics", body)
        self.assertNotIn("profile", body)
        self.assertEqual(body["claim_classification"], "speculative")

    def test_report_does_not_expose_observation_or_note_bodies(self):
        body, status, _ = self.get_json("/api/report")
        self.assertEqual(status, 200)
        self.assertEqual(body["observations_count"], 0)
        self.assertNotIn("notes", body)

    def test_invalid_interval_is_a_client_error(self):
        body, status, _ = self.get_json("/api/interval?dt=nan&dx=1")
        self.assertEqual(status, 400)
        self.assertFalse(body["ok"])

    def test_dashboard_is_read_only(self):
        request = Request(self.base + "/api/health", data=b"{}", method="POST")
        with self.assertRaises(HTTPError) as caught:
            urlopen(request, timeout=3)
        self.assertEqual(caught.exception.code, 405)

    def test_arbitrary_route_is_not_found(self):
        body, status, _ = self.get_json("/etc/passwd")
        self.assertEqual(status, 404)
        self.assertFalse(body["ok"])

    def test_oversized_profile_is_rejected(self):
        body, status, _ = self.get_json("/api/profile?radius=10&sigma=1&samples=50000")
        self.assertEqual(status, 400)
        self.assertIn("must not exceed", body["error"])


if __name__ == "__main__":
    unittest.main()
