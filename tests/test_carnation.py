import unittest

from src.cognition.carnation import (
    CarnationState,
    EpistemicStatus,
    WitnessState,
    build_soul_tag,
    normalize_components,
    project_expression,
)


class CarnationTests(unittest.TestCase):
    def test_normalize_superposition(self):
        state = normalize_components(
            {
                WitnessState.WITNESS: 2,
                WitnessState.ARCHIVIST: 1,
                WitnessState.UNKNOWN: 1,
            }
        )
        self.assertEqual(round(sum(item.weight for item in state.components), 6), 1.0)
        self.assertIs(state.dominant().state, WitnessState.WITNESS)

    def test_projection_error_is_separate_from_witness_state(self):
        state = normalize_components({
            WitnessState.WITNESS: 0.5,
            WitnessState.ARCHIVIST: 0.5,
        })
        projection = project_expression(
            state,
            "rendered voice",
            [WitnessState.WITNESS],
            fidelity=0.4,
            missing_states=[WitnessState.ARCHIVIST],
            distortion_tags=["style-drift"],
        )
        self.assertEqual(projection.fidelity, 0.4)
        self.assertEqual(projection.projection_error, 0.6)
        self.assertEqual(projection.missing_states, (WitnessState.ARCHIVIST,))

    def test_maximal_soul_tag_is_provenance_rich_not_metaphysical(self):
        state = normalize_components({WitnessState.EVEZ: 1.0})
        tag = build_soul_tag(
            continuity_id="cont-001",
            lineage_id="line-001",
            manifestation_id="manifest-001",
            soul_tag="EVEZ:CONT-001",
            carnation_state=CarnationState.INCARNATION,
            witness_superposition=state,
            person_frame="Steven Crawford-Maggard",
            identity_frame="EVEZ666",
            artifact_frame="EVEZ-OS",
            epistemic_status=EpistemicStatus.PROPOSED,
            tags={"domain": "crystalinformergence"},
        )
        payload = tag.as_dict()
        self.assertEqual(payload["soul_tag"], "EVEZ:CONT-001")
        self.assertEqual(payload["epistemic_status"], "PROPOSED")


if __name__ == "__main__":
    unittest.main()
