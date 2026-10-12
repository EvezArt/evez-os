import importlib.util
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import threading
import unittest
from urllib.request import urlopen

from evez_epie.kernel import EventLedger
from evez_epie.spine_adapter import (
    _base_url,
    _request_json,
    sync_ledger_to_spine,
    verify_spine,
)

MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "services" / "event_spine.py"
spec = importlib.util.spec_from_file_location("evez_event_spine_adapter_test", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SpineAdapterIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.previous_spine = module.SPINE
        module.SPINE = module.EventSpine()
        self.server = module.HTTPServer(("127.0.0.1", 0), module.Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        module.SPINE = self.previous_spine

    @staticmethod
    def sample_ledger():
        ledger = EventLedger()
        ledger.append("OBSERVED_FACT", {"claim_status": "REPORTED", "claim_id": "c1"})
        ledger.append("EVIDENCE_COMMIT", {"source_hash": "a" * 64, "claim_id": "c1"})
        ledger.append("CHECKPOINT_ISSUED", {"case_id": "case-1", "result": "UNKNOWN"})
        return ledger

    def test_sync_is_verified_and_retry_safe(self):
        ledger = self.sample_ledger()
        first = sync_ledger_to_spine(ledger, base_url=self.base_url)
        self.assertTrue(first["valid"])
        self.assertEqual(first["appended_count"], 3)
        self.assertEqual(first["already_present_count"], 0)
        self.assertTrue(first["verification"]["valid"])
        self.assertEqual(len(module.SPINE.events), 3)

        second = sync_ledger_to_spine(ledger, base_url=self.base_url)
        self.assertTrue(second["valid"])
        self.assertEqual(second["appended_count"], 0)
        self.assertEqual(second["already_present_count"], 3)
        self.assertEqual(len(module.SPINE.events), 3)

    def test_tampered_remote_content_is_reported(self):
        sync_ledger_to_spine(self.sample_ledger(), base_url=self.base_url)
        module.SPINE._events[0]["data"]["event"]["payload"]["claim_status"] = "VERIFIED"
        result = verify_spine(base_url=self.base_url)
        self.assertFalse(result["valid"])
        self.assertTrue(result["errors"])

    def test_query_parameter_routes_work(self):
        module.SPINE.append("epie", "OBSERVED_FACT", {"v": 1})
        with urlopen(self.base_url + "/recent?n=1", timeout=2) as response:
            recent = json.loads(response.read().decode("utf-8"))
        self.assertEqual(recent["count"], 1)
        with urlopen(self.base_url + "/replay?domain=epie", timeout=2) as response:
            replay = json.loads(response.read().decode("utf-8"))
        self.assertEqual(replay["count"], 1)
        self.assertEqual(replay["domain"], "epie")

    def test_redirects_are_rejected(self):
        class RedirectHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(302)
                self.send_header("Location", "https://example.com/redirected")
                self.end_headers()

            def log_message(self, format, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), RedirectHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_port}"
            with self.assertRaisesRegex(RuntimeError, "HTTP 302"):
                _request_json(url, "/health", timeout=2)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_remote_http_target_is_blocked_by_default(self):
        with self.assertRaisesRegex(PermissionError, "allow_remote"):
            _base_url("http://example.com:9116", allow_remote=False)
        with self.assertRaisesRegex(PermissionError, "HTTPS"):
            _base_url("http://example.com:9116", allow_remote=True)
        self.assertEqual(_base_url(self.base_url, allow_remote=False), self.base_url)


if __name__ == "__main__":
    unittest.main()
