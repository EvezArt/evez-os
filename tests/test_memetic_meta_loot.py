import unittest
from mobile.evez_memetic_meta_loot import run


class MemeticMetaLootTests(unittest.TestCase):
    def test_loots_permaloot(self):
        source = {
            "permaloot_architecture_sha256": "abc",
            "inventory": [
                {"loot_id": "a", "layer": 1, "kind": "META_DISCOVERY", "payload": {}, "parent_ids": []},
                {"loot_id": "b", "layer": 1, "kind": "NEXT_FRONTIER", "payload": {}, "parent_ids": ["a"]},
                {"loot_id": "c", "layer": 1, "kind": "BOUNDARY_DISCOVERY", "payload": {}, "parent_ids": ["a"]},
            ],
        }
        result = run(source)
        self.assertGreaterEqual(result["memetic_inventory_count"], 3)
        self.assertEqual(result["source_architecture_sha256"], "abc")
        for meme in result["memes"]:
            self.assertTrue(meme["source_loot_ids"])
            self.assertEqual(meme["status"], "GENERATED_FROM_OBSERVABLE_LOOT")

    def test_deterministic(self):
        source = {
            "permaloot_architecture_sha256": "abc",
            "inventory": [{"loot_id": "x", "layer": 1, "kind": "NEXT_FRONTIER", "payload": {}, "parent_ids": []}],
        }
        self.assertEqual(run(source)["memetic_meta_loot_sha256"], run(source)["memetic_meta_loot_sha256"])


if __name__ == "__main__":
    unittest.main()
