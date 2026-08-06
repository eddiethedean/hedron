"""Phase 0.18 SCENARIO-018: ModelDemoScenario kit."""

from __future__ import annotations

import pytest

from hedron_core.testing import AppScenario, ModelDemoScenario


def _noop_get(path: str, *, headers=None, cookies=None):  # type: ignore[no-untyped-def]
    from hedron_core.testing.adapters import AdapterResponse

    return AdapterResponse(status_code=200, body="<html></html>", headers={}, cookies={})


def _noop_post(path: str, *, data=None, headers=None, cookies=None):  # type: ignore[no-untyped-def]
    return _noop_get(path)


def test_synthetic_files_and_no_real_model() -> None:
    app = AppScenario.from_callables(_noop_get, _noop_post)
    scenario = ModelDemoScenario(app=app)
    scenario.add_synthetic_file("sample.txt", b"hello")
    scenario.add_synthetic_result("r1", {"label": "cat", "score": 0.9})
    scenario.record_admission("queued")
    scenario.record_progress({"pct": 50})
    scenario.record_cancellation("inf-1")
    scenario.grant_consent()
    scenario.mark_redacted("password", "token")
    scenario.retain("fb-1")
    scenario.assert_consent_required()
    scenario.assert_redaction("password", "token")
    scenario.assert_retention_deletable("fb-1")
    scenario.assert_no_real_model_loaded()
    assert scenario.admissions == ["queued"]
    assert scenario.progress_events[0]["pct"] == 50
    assert scenario.cancellations == ["inf-1"]


def test_rejects_oversized_and_trusted_output() -> None:
    app = AppScenario.from_callables(_noop_get, _noop_post)
    scenario = ModelDemoScenario(app=app, max_file_bytes=4)
    with pytest.raises(AssertionError, match="max_file_bytes"):
        scenario.add_synthetic_file("big.bin", b"12345")
    scenario.trust_generated_output = True
    with pytest.raises(AssertionError, match="trustworthy"):
        scenario.add_synthetic_result("bad", {"x": 1})
