import tempfile, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from energy_witness.core import EnergyWitness, Meter, VerificationError, sign_reading

class EnergyWitnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); now=datetime.now(timezone.utc); self.secret=b"test-only-secret"
        meter=Meter("M-001","operator-1",self.secret,"active",(now-timedelta(days=1)).isoformat(),(now+timedelta(days=30)).isoformat())
        self.witness=EnergyWitness(Path(self.tmp.name)/"ledger.jsonl",{"M-001":meter})
        end=now-timedelta(minutes=1); start=end-timedelta(minutes=15)
        self.reading={"reading_id":"R-001","meter_id":"M-001","operator_id":"operator-1","interval_start":start.isoformat(),"interval_end":end.isoformat(),"export_wh":1000,"cumulative_export_wh":1000,"evidence_source":"certified_meter_attestation"}
        self.reading["signature"]=sign_reading(self.reading,self.secret)
    def tearDown(self): self.tmp.cleanup()
    def test_valid_reading_records_one_kwh_without_reward(self):
        result=self.witness.submit(self.reading); self.assertEqual(result["export_kwh"],1.0)
        self.assertEqual(result["reward_status"],"NOT_ISSUED_PENDING_INDEPENDENT_SETTLEMENT")
        self.assertEqual(len(self.witness._existing()),1)
    def test_duplicate_rejected(self):
        self.witness.submit(self.reading)
        with self.assertRaisesRegex(VerificationError,"duplicate"): self.witness.submit(self.reading)
    def test_tampering_rejected(self):
        self.reading["export_wh"]=999999
        with self.assertRaisesRegex(VerificationError,"signature"): self.witness.submit(self.reading)
    def test_operator_claim_rejected(self):
        self.reading["evidence_source"]="operator_claim"; self.reading["signature"]=sign_reading(self.reading,self.secret)
        with self.assertRaisesRegex(VerificationError,"evidence source"): self.witness.submit(self.reading)

if __name__=="__main__": unittest.main()
