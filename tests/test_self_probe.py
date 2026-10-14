from rqns.audit.self_probe import probe_current_reasoning


def test_self_probe_is_explicit_and_falsifiable():
    result = probe_current_reasoning()
    assert result.subject == "assistant reasoning process"
    assert result.claim
    assert result.observable
    assert result.test
    assert result.falsifier
    assert result.current_state == "SUPPORTED"
    assert "No runtime test execution is claimed" in result.unresolved[0]
