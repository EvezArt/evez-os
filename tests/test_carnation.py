from src.cognition.carnation import (
    CarnationState,
    EpistemicStatus,
    WitnessState,
    build_soul_tag,
    normalize_components,
    project_expression,
)


def test_normalize_superposition():
    state = normalize_components(
        {
            WitnessState.WITNESS: 2,
            WitnessState.ARCHIVIST: 1,
            WitnessState.UNKNOWN: 1,
        }
    )
    assert round(sum(item.weight for item in state.components), 6) == 1.0
    assert state.dominant().state is WitnessState.WITNESS


def test_projection_error_is_separate_from_witness_state():
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
    assert projection.fidelity == 0.4
    assert projection.projection_error == 0.6
    assert projection.missing_states == (WitnessState.ARCHIVIST,)


def test_maximal_soul_tag_is_provenance_rich_not_metaphysical():
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
    assert payload["soul_tag"] == "EVEZ:CONT-001"
    assert payload["epistemic_status"] == "PROPOSED"
