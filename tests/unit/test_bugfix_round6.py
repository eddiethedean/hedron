"""Regression tests for the top-20 correctness and validation audit."""

from __future__ import annotations

from datetime import date

import pytest

from hedron.config import load_hedron_settings
from hedron_charts.compile import apply_transforms
from hedron_charts.spec import TransformDef
from hedron_core.a11y.governance import HumanAtRecord
from hedron_core.builtins.media import Video
from hedron_core.builtins.model_demo import PredictionLabel
from hedron_core.diagnostics import HedronError
from hedron_core.jobs.codec import _status_from_dict
from hedron_core.testing.workbench import assert_action_authorized
from hedron_data.views import SavedView


@pytest.mark.parametrize(
    "overrides",
    [
        {"format_version": True},
        {"component_roots": "components"},
        {"plugins": "plugin"},
        {"compiler_checks": "false"},
        {"build_dir": 7},
        {"theme": 7},
        {"explorer": False},
        {"diagnostic_severities": []},
        {"asset_policy": []},
        {"asset_policy": {"allow_remote": "false"}},
        {"asset_policy": {"strict_csp": 1}},
        {"asset_policy": {"reject_inline_style": "true"}},
        {"asset_policy": {"registered_roots": "assets"}},
    ],
)
def test_config_rejects_values_that_were_silently_reinterpreted(
    overrides: dict[str, object],
) -> None:
    with pytest.raises(HedronError, match="HED-CONFIG"):
        load_hedron_settings(overrides=overrides)


def _human_record(**updates: object) -> dict[str, object]:
    row: dict[str, object] = {
        "record_id": "r1",
        "gate_ids": ["PROTOCOL-021"],
        "combo_id": "vo-safari-macos",
        "os": {"name": "macOS", "version": "15"},
        "browser": {"name": "Safari", "version": "18"},
        "at": {"name": "VoiceOver", "version": "15"},
        "task_id": "login",
        "result": "pass",
        "owner": "a11y",
        "retest_date": date.today().isoformat(),
        "redacted": True,
    }
    row.update(updates)
    return row


@pytest.mark.parametrize(
    ("key", "value"),
    [("gate_ids", "PROTOCOL-021"), ("task_ids", "login"), ("redacted", "true"), ("stretch", 1)],
)
def test_human_at_record_rejects_scalar_collection_and_boolean_coercion(
    key: str, value: object
) -> None:
    with pytest.raises(ValueError):
        HumanAtRecord.from_dict(_human_record(**{key: value}))


def test_job_codec_rejects_truthy_string_cancel_flag() -> None:
    with pytest.raises(ValueError, match="cancel_requested"):
        _status_from_dict(
            {
                "job_id": "j1",
                "state": "queued",
                "job_type": "demo",
                "cancel_requested": "false",
            }
        )


def test_workbench_fixture_authorization_fails_closed_on_non_boolean() -> None:
    with pytest.raises(AssertionError, match="must be a boolean"):
        assert_action_authorized({"authorized": "false"})


def test_prediction_score_rejects_truthy_string_calibration() -> None:
    with pytest.raises(ValueError, match="calibrated"):
        PredictionLabel([{"class_id": "cat", "score": 0.8, "calibrated": "false"}])


@pytest.mark.parametrize("field", ["reviewed", "default"])
def test_media_tracks_reject_non_boolean_flags(field: str) -> None:
    video = Video("/video.mp4", tracks=[{"kind": "captions", "src": "/c.vtt", field: "false"}])
    with pytest.raises(ValueError, match=field):
        video.render()


@pytest.mark.parametrize(("op", "params"), [("sample", {"n": 0}), ("bin", {"bins": 0})])
def test_chart_zero_bounds_are_rejected_instead_of_defaulted(
    op: str, params: dict[str, object]
) -> None:
    with pytest.raises(HedronError):
        apply_transforms([{"x": 1}], [TransformDef(op=op, field="x", params=params)])


def test_chart_sort_rejects_string_boolean() -> None:
    with pytest.raises(HedronError, match="HED-CHART-0072"):
        apply_transforms([{"x": 1}], [TransformDef(op="sort", field="x", params={"desc": "false"})])


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "view", "columns": "id"},
        {"name": "view", "selection": "row-1"},
        {"name": "view", "filters": []},
        {"name": "view", "sort": ["name", "asc"]},
    ],
)
def test_saved_view_rejects_malformed_collection_shapes(payload: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        SavedView.deserialize(payload)
