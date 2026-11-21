import unittest

from src.services.observer_externality import (
    EXTERNAL_SOURCES, InteractionTrace, Observation, audit_trace,
    decide_promotion, invariant_snapshot,
)

class ObserverExternalityTests(unittest.TestCase):
    def test_model_output_cannot_self_confirm(self):
        obs = Observation("o1","initial","model_output",external=False)
        later = Observation("o2","confirmed","model_output",external=False,parent_ids=("o1",))
        trace = InteractionTrace("t1",obs,"this means X","is X true?","yes","looks confirmed",later)
        findings = audit_trace(trace)
        codes = {f.code for f in findings}
        self.assertIn("INTERNAL_ORIGIN", codes)
        self.assertIn("MODEL_DERIVED_OBSERVATION", codes)
        self.assertEqual(sum(f.evidence_weight for f in findings), 0)
        decision = decide_promotion("claim-1","UNKNOWN","SUPPORTED",[obs,later])
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.evidence_weight, 0)
        self.assertTrue(decision.self_confirmation)

    def test_external_state_transition_can_enter_gate(self):
        original = Observation("o1","before","human_observer",source_ref="field-note-1",external=True)
        subsequent = Observation("o2","after","government_record",source_ref="record-1",external=True)
        trace = InteractionTrace("t2",original,"possible explanation","check the record","search result summary","inspect source",subsequent)
        findings = audit_trace(trace)
        self.assertIn("EXTERNAL_STATE_TRANSITION",{f.code for f in findings})
        decision = decide_promotion("claim-2","PROPOSED","SUPPORTED",[original,subsequent])
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.evidence_weight, 2)
        self.assertEqual(decision.external_observation_ids,("o1","o2"))

    def test_unknown_provenance_does_not_count(self):
        unknown = Observation("o1","maybe","unknown_adapter",external=False)
        decision = decide_promotion("claim-3","UNKNOWN","SUPPORTED",[unknown])
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.evidence_weight, 0)

    def test_invariant_is_machine_readable(self):
        snap = invariant_snapshot()
        self.assertEqual(snap["id"],"EXTERNALITY")
        self.assertTrue(snap["equations"]["MODEL_OUTPUT_CANNOT_VALIDATE_ITS_OWN_PREMISES"])
        self.assertEqual(snap["equations"]["internal_evidence_weight"],0)
        self.assertIn("government_record",EXTERNAL_SOURCES)

if __name__ == "__main__":
    unittest.main()
