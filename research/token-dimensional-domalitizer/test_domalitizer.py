import json
import tempfile
import unittest
from pathlib import Path

from domalitizer import analyze, normalize_token, validate_lexicon


class DomalitizerTests(unittest.TestCase):
    def test_round_trip_offsets_preserve_source(self):
        source = "EVEZ: tokendimensional domalitizing domain."
        result = analyze(source)
        self.assertTrue(result["round_trip"]["token_spans_valid"])
        self.assertTrue(result["round_trip"]["exact_source_preserved"])
        self.assertEqual(result["domalitization"]["tensor_shape"], [len(result["tokens"]), 8, 8])
        self.assertEqual(len(result["domain_coactivation"]), 8)
        self.assertEqual(len(result["tokens"][0]["domain_tensor"]["matrix"]), 8)
        for token in result["tokens"]:
            start, end = token["span"]
            self.assertEqual(source[start:end], token["surface"])

    def test_unknowns_remain_unknown(self):
        result = analyze("unseenlexeme")
        dims = result["tokens"][0]["dimensions"]
        self.assertEqual(dims["etymological"]["status"], "UNKNOWN")
        self.assertIsNone(dims["etymological"]["origin"])

    def test_user_gloss_is_not_attested_etymology(self):
        lexicon = {
            "domalitizing": {
                "semantic": {"glosses": ["domain mapping"], "status": "USER_SUPPLIED"}
            }
        }
        result = analyze("domalitizing", lexicon)
        dims = result["tokens"][0]["dimensions"]
        self.assertEqual(dims["semantic"]["status"], "USER_SUPPLIED")
        self.assertEqual(dims["etymological"]["status"], "UNKNOWN")

    def test_normalization(self):
        self.assertEqual(normalize_token("DOMALITIZING"), "domalitizing")

    def test_lexicon_validation(self):
        payload = {"domalitizing": {"semantic": {"glosses": ["domain mapping"]}}}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lexicon.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(len(validate_lexicon(path)), 1)


if __name__ == "__main__":
    unittest.main()
