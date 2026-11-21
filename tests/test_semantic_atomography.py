from rqns.audit.semantic_atomography import SemanticAtom, SemanticTomograph


def test_nested_agent_llm_agent_trace_is_observable():
    trace = SemanticTomograph()
    trace.add(
        SemanticAtom(
            atom_id="a0",
            parent_id=None,
            actor_id="agent-root",
            kind="agent",
            input_text="solve the task",
            output_text="delegate semantic analysis",
            depth=0,
        )
    )
    trace.add(
        SemanticAtom(
            atom_id="a1",
            parent_id="a0",
            actor_id="llm-1",
            kind="llm",
            input_text="delegate semantic analysis",
            output_text="spawn an analyst agent",
            depth=1,
        )
    )
    trace.add(
        SemanticAtom(
            atom_id="a2",
            parent_id="a1",
            actor_id="agent-analyst",
            kind="agent",
            input_text="spawn an analyst agent",
            output_text="return a measured distinction",
            depth=2,
        )
    )

    assert trace.max_depth() == 2
    assert len(trace.recursive_handoffs()) == 2
    assert trace.summary()["atom_count"] == 3
    assert len(trace.snapshot_hash()) == 64


def test_unknown_parent_is_rejected():
    trace = SemanticTomograph()
    try:
        trace.add(
            SemanticAtom(
                atom_id="orphan",
                parent_id="missing",
                actor_id="agent",
                kind="agent",
                input_text="x",
                output_text="y",
                depth=1,
            )
        )
    except ValueError as exc:
        assert "unknown parent" in str(exc)
    else:
        raise AssertionError("unknown semantic parent was accepted")


def test_same_language_can_change_semantic_features():
    atom = SemanticAtom(
        atom_id="a",
        parent_id=None,
        actor_id="llm",
        kind="llm",
        input_text="model update disabled",
        output_text="learning persists without update",
    )
    added, removed = atom.semantic_delta
    assert "persists" in added
    assert "disabled" in removed
