from mobile.evez_unlock import UnlockState, calculate_unlocks, result_payload


BASE = {
    "device": {"present": True},
    "storage": {"writable": True},
    "network": {"available": True},
    "sync": {"endpoint_configured": True},
    "runtime": {"healthy": True},
    "evidence": {"chain_status": "VERIFIED"},
    "authorization": {"state": "AUTHORIZED"},
    "rollback": {"available": True},
    "tests": {"passed": True},
    "artifact": {"provenance_complete": True},
    "voice": {"model_available": True},
    "music": {"engine_available": True},
    "policy": {"explicit_allow": True},
    "execution": {"mode": "NORMAL"},
}


def test_full_context_unlocks():
    results = calculate_unlocks(BASE)
    assert results["observe.local"].state == UnlockState.UNLOCKED
    assert results["witness.write"].state == UnlockState.UNLOCKED
    assert results["evidence.sync"].state == UnlockState.UNLOCKED
    assert results["pipeline.run"].state == UnlockState.UNLOCKED
    assert results["self.modify"].state == UnlockState.UNLOCKED
    assert results["deploy.remote"].state == UnlockState.UNLOCKED
    assert results["autonomous.execute"].state == UnlockState.UNLOCKED


def test_unknown_does_not_become_permission():
    context = dict(BASE)
    context["evidence"] = {"chain_status": "UNKNOWN"}
    results = calculate_unlocks(context)
    assert results["witness.write"].state == UnlockState.LOCKED
    assert results["self.modify"].state == UnlockState.LOCKED


def test_failed_test_locks_modify():
    context = dict(BASE)
    context["tests"] = {"passed": False}
    results = calculate_unlocks(context)
    assert results["self.modify"].state == UnlockState.LOCKED
    assert results["deploy.remote"].state == UnlockState.LOCKED


def test_dry_run_is_explicit_alternative():
    context = dict(BASE)
    context["policy"] = {"explicit_allow": False}
    context["execution"] = {"mode": "DRY_RUN"}
    results = calculate_unlocks(context)
    assert results["autonomous.execute"].state == UnlockState.UNLOCKED


def test_result_has_stable_digest():
    payload = result_payload(calculate_unlocks(BASE))
    assert len(payload["calculation_sha256"]) == 64
