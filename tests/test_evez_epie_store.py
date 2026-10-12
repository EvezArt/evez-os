import concurrent.futures
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest

from evez_epie import JsonlLedgerStore


class JsonlLedgerStoreTests(unittest.TestCase):
    def test_durable_roundtrip_and_private_permissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "evidence.jsonl"
            store = JsonlLedgerStore(path)
            store.append("OBSERVED_FACT", {"claim_status": "REPORTED", "claim_id": "c1"})
            store.append("EVIDENCE_COMMIT", {"source_hash": "a" * 64})
            loaded = store.load()
            self.assertEqual(loaded.verify(), (True, "ok"))
            self.assertEqual(loaded.replay()["event_count"], 2)
            self.assertTrue(path.read_bytes().endswith(b"\n"))
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_content_tamper_is_rejected_on_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.jsonl"
            store = JsonlLedgerStore(path)
            store.append("OBSERVED_FACT", {"claim_status": "REPORTED"})
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace("REPORTED", "ALTERED"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Invalid initial ledger"):
                store.load()
            self.assertFalse(store.verify()[0])

    def test_partial_final_line_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.jsonl"
            store = JsonlLedgerStore(path)
            store.append("OBSERVED_FACT", {"x": 1})
            with path.open("ab") as stream:
                stream.write(b'{"partial":')
            with self.assertRaisesRegex(ValueError, "incomplete final line"):
                store.load()
            # It must not silently truncate the incomplete evidence record.
            self.assertTrue(path.read_bytes().endswith(b'{"partial":'))

    def test_parallel_writers_preserve_one_valid_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "shared.jsonl"
            stores = [JsonlLedgerStore(path) for _ in range(4)]

            def write_batch(worker):
                store = stores[worker]
                for offset in range(10):
                    store.append("OBSERVED_FACT", {"worker": worker, "offset": offset})

            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(write_batch, range(4)))

            ledger = JsonlLedgerStore(path).load()
            self.assertEqual(ledger.verify(), (True, "ok"))
            self.assertEqual(ledger.replay()["event_count"], 40)
            self.assertEqual([event["sequence"] for event in ledger.events], list(range(40)))

    def test_ledger_symlink_is_not_followed(self):
        if not hasattr(os, "O_NOFOLLOW"):
            self.skipTest("O_NOFOLLOW is not available on this platform")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target.jsonl"
            target.write_text("", encoding="utf-8")
            link = root / "linked.jsonl"
            link.symlink_to(target)
            store = JsonlLedgerStore(link)
            with self.assertRaisesRegex(ValueError, "symlink"):
                store.load()


if __name__ == "__main__":
    unittest.main()
