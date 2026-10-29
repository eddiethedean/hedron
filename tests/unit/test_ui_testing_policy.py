"""Security and identity regressions for the optional UI testing layer."""

# These tests exercise private policy seams with small native-object stand-ins.
# pyright: reportPrivateUsage=false

from __future__ import annotations

from collections import deque
from pathlib import Path
from types import SimpleNamespace
from typing import cast, final

import pytest
from playwright.sync_api import Route

from hedron.testing._ui_testing.scenario import (
    AmbiguousSettleError,
    BrowserScenario,
    BrowserScenarioFactory,
    Checkpoint,
    InvalidCheckpointError,
)
from hedron.testing.pytest_plugin import (
    _validate_capture_context_args,
    _validate_capture_options,
)


@pytest.mark.parametrize("option", ["record_har_path", "record_video_dir"])
def test_raw_context_recording_is_rejected(option: str) -> None:
    with pytest.raises(pytest.UsageError, match="do not permit HAR or video"):
        _validate_capture_context_args({option: "/tmp/raw-output"})


def test_empty_raw_context_recording_options_are_allowed() -> None:
    _validate_capture_context_args({"record_har_path": None, "record_video_dir": None})


def test_upstream_capture_flags_require_synthetic_consent_before_context_creation() -> None:
    config = _capture_config(
        {
            "--tracing": "retain-on-failure",
            "--screenshot": "off",
            "--video": "off",
            "--full-page-screenshot": False,
        }
    )

    with pytest.raises(pytest.UsageError, match="restricted to tests marked"):
        _validate_capture_options(config, ("structured", False))


def test_explicit_synthetic_capture_accepts_only_the_admitted_options(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("HEDRON_UI_CAPTURE_BUDGET", "linux-tmpfs-128m-monitor-25ms-file-64m-v1")
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    config = _capture_config(
        {
            "--tracing": "retain-on-failure",
            "--screenshot": "only-on-failure",
            "--video": "off",
            "--full-page-screenshot": False,
            "--output": str(tmp_path / "playwright-output"),
        }
    )
    _validate_capture_options(config, ("synthetic", True))

    unbounded_config = _capture_config(
        {
            "--tracing": "retain-on-failure",
            "--screenshot": "off",
            "--video": "on",
            "--full-page-screenshot": False,
            "--output": str(tmp_path / "playwright-output"),
        }
    )
    with pytest.raises(pytest.UsageError, match="video and full-page capture are not admitted"):
        _validate_capture_options(unbounded_config, ("synthetic", True))


def test_synthetic_capture_requires_the_monitored_linux_budget_runner(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("HEDRON_UI_CAPTURE_BUDGET", raising=False)
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    config = _capture_config(
        {
            "--tracing": "retain-on-failure",
            "--screenshot": "off",
            "--video": "off",
            "--full-page-screenshot": False,
            "--output": str(tmp_path / "playwright-output"),
        }
    )
    with pytest.raises(pytest.UsageError, match="requires Hedron's Linux budget runner"):
        _validate_capture_options(config, ("synthetic", True))


def test_synthetic_capture_output_must_stay_inside_private_tmpdir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("HEDRON_UI_CAPTURE_BUDGET", "linux-tmpfs-128m-monitor-25ms-file-64m-v1")
    private_tmp = tmp_path / "private"
    private_tmp.mkdir()
    monkeypatch.setenv("TMPDIR", str(private_tmp))
    config = _capture_config(
        {
            "--tracing": "retain-on-failure",
            "--screenshot": "off",
            "--video": "off",
            "--full-page-screenshot": False,
            "--output": str(tmp_path / "public-output"),
        }
    )
    with pytest.raises(pytest.UsageError, match="--output inside private TMPDIR"):
        _validate_capture_options(config, ("synthetic", True))


def _capture_config(options: dict[str, object]) -> pytest.Config:
    return cast(
        pytest.Config,
        cast(object, SimpleNamespace(getoption=lambda name: options[name])),
    )


def test_checkpoint_from_sibling_scenario_is_rejected() -> None:
    owner = cast(
        BrowserScenarioFactory,
        cast(object, SimpleNamespace(_session_id="fixture-session")),
    )
    first = BrowserScenario.__new__(BrowserScenario)
    second = BrowserScenario.__new__(BrowserScenario)
    first._owner = owner
    second._owner = owner
    first._session_id = "scenario-one"
    second._session_id = "scenario-two"
    second._navigation_epoch = 1

    checkpoint = Checkpoint("scenario-one", 1, 0, "document", 0, 0)

    with pytest.raises(InvalidCheckpointError, match="different browser scenario"):
        second._validate_checkpoint(checkpoint)


def test_settle_rejects_invalid_generation_and_action_filter_before_page_use() -> None:
    scenario = BrowserScenario.__new__(BrowserScenario)
    scenario._session_id = "scenario"
    scenario._navigation_epoch = 0
    checkpoint = Checkpoint("scenario", 0, 0, "document", 0, 0)

    with pytest.raises(ValueError, match="generation must be a non-negative integer"):
        scenario.settle(since=checkpoint, target="result", generation=True)
    with pytest.raises(TypeError, match="user_action must be a boolean or None"):
        scenario.settle(since=checkpoint, target="result", user_action=1)  # type: ignore[arg-type]


def test_ambiguous_settle_error_is_publicly_exported() -> None:
    from hedron.testing.browser_scenario import AmbiguousSettleError as PublicAmbiguousSettleError

    assert PublicAmbiguousSettleError is AmbiguousSettleError


def test_redirect_response_is_blocked_before_browser_followup() -> None:
    scenario = BrowserScenario.__new__(BrowserScenario)
    scenario._allowed_origins = frozenset({"http://127.0.0.1:8000"})
    scenario._categories = deque(maxlen=16)

    def record_error(_category: str) -> None:
        return None

    scenario._owner = cast(
        BrowserScenarioFactory,
        cast(object, SimpleNamespace(_record_error=record_error)),
    )
    route = _RedirectRoute()

    scenario._route_request(cast(Route, cast(object, route)))

    assert route.fetch_args == {"max_redirects": 0}
    assert route.aborted is True
    assert route.fulfilled is False
    assert route.response.disposed is True
    assert "redirect_blocked" in scenario._categories


def test_routed_success_disposes_response_after_fulfill() -> None:
    scenario = _policy_scenario()
    response = _RouteResponse(status=200)
    route = _PolicyRoute(response)

    scenario._route_request(cast(Route, cast(object, route)))

    assert route.fulfilled is True
    assert route.aborted is False
    assert response.disposed is True


def test_routed_fulfill_failure_aborts_and_disposes_response() -> None:
    scenario = _policy_scenario()
    response = _RouteResponse(status=200)
    route = _PolicyRoute(response, fail_fulfill=True)

    scenario._route_request(cast(Route, cast(object, route)))

    assert route.fulfilled is True
    assert route.aborted is True
    assert response.disposed is True
    assert "request_policy_failure" in scenario._categories


def _policy_scenario() -> BrowserScenario:
    scenario = BrowserScenario.__new__(BrowserScenario)
    scenario._allowed_origins = frozenset({"http://127.0.0.1:8000"})
    scenario._categories = deque(maxlen=16)
    scenario._owner = cast(
        BrowserScenarioFactory,
        cast(object, SimpleNamespace(_record_error=lambda _category: None)),
    )
    return scenario


@final
class _RedirectRoute:
    def __init__(self) -> None:
        self.request: object = SimpleNamespace(url="http://127.0.0.1:8000/redirect")
        self.response = _RouteResponse(status=302)
        self.fetch_args: dict[str, object] | None = None
        self.aborted: bool = False
        self.fulfilled: bool = False

    def fetch(self, **kwargs: object) -> object:
        self.fetch_args = kwargs
        return self.response

    def abort(self, _error: str) -> None:
        self.aborted = True

    def fulfill(self, *, response: object) -> None:
        del response
        self.fulfilled = True


@final
class _PolicyRoute:
    def __init__(self, response: _RouteResponse, *, fail_fulfill: bool = False) -> None:
        self.request: object = SimpleNamespace(
            url="http://127.0.0.1:8000/profile",
            header_value=lambda _name: "",
        )
        self.response = response
        self.fail_fulfill = fail_fulfill
        self.aborted = False
        self.fulfilled = False

    def fetch(self, **_kwargs: object) -> _RouteResponse:
        return self.response

    def abort(self, _error: str) -> None:
        self.aborted = True

    def fulfill(self, *, response: object) -> None:
        assert response is self.response
        self.fulfilled = True
        if self.fail_fulfill:
            raise RuntimeError("synthetic fulfill failure")


@final
class _RouteResponse:
    def __init__(self, *, status: int) -> None:
        self.status = status
        self.disposed = False

    def dispose(self) -> None:
        self.disposed = True
