"""Regression coverage for production-quality Phase 1 exception/logging fixes."""

from __future__ import annotations

import logging
import sys
import types

import pytest
from flask import session

from hedron.connections import ConnectionRegistry
from hedron_core.jobs_rq import RQJobBackend
from hedron_flask import HedronFlask


def test_connection_health_logs_factory_failure(caplog: pytest.LogCaptureFixture) -> None:
    registry = ConnectionRegistry()

    def boom() -> object:
        raise RuntimeError("factory exploded")

    registry.register("db", boom)
    with caplog.at_level(logging.ERROR, logger="hedron.connections"):
        assert registry.health("db") is False
    assert any("factory failed" in record.message for record in caplog.records)


def test_connection_health_logs_healthcheck_failure(caplog: pytest.LogCaptureFixture) -> None:
    registry = ConnectionRegistry()

    def bad_check(_conn: object) -> bool:
        raise ValueError("bad")

    registry.register("db", lambda: object(), healthcheck=bad_check)
    with caplog.at_level(logging.ERROR, logger="hedron.connections"):
        assert registry.health("db") is False
    assert any("healthcheck raised" in record.message for record in caplog.records)


def test_flask_auth_signal_falls_back_when_flask_login_raises(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    class _BrokenUser:
        @property
        def is_authenticated(self) -> bool:
            raise RuntimeError("no request context")

    fake = types.ModuleType("flask_login")
    fake.current_user = _BrokenUser()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "flask_login", fake)

    hedron = HedronFlask(__name__)
    app = hedron.flask
    assert app is not None
    app.secret_key = "test"
    with app.test_request_context("/"):
        session["user_id"] = "session-user"
        with caplog.at_level(logging.DEBUG, logger="hedron.flask"):
            signal = hedron.auth_signal()
    assert signal.authenticated is True
    assert signal.subject_id == "session-user"
    assert any("flask_login" in record.message for record in caplog.records)


def _install_fake_rq(monkeypatch: pytest.MonkeyPatch, *, fetch_raises: BaseException) -> None:
    no_such = type("NoSuchJobError", (Exception,), {})
    exceptions = types.ModuleType("rq.exceptions")
    exceptions.NoSuchJobError = no_such  # type: ignore[attr-defined]

    class _Job:
        @staticmethod
        def fetch(*_a: object, **_k: object) -> object:
            raise fetch_raises

    job_mod = types.ModuleType("rq.job")
    job_mod.Job = _Job  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "rq", types.ModuleType("rq"))
    monkeypatch.setitem(sys.modules, "rq.exceptions", exceptions)
    monkeypatch.setitem(sys.modules, "rq.job", job_mod)


def test_rq_fetch_missing_job_returns_none_without_warning(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    no_such = type("NoSuchJobError", (Exception,), {})
    _install_fake_rq(monkeypatch, fetch_raises=no_such("missing"))
    # Keep except NoSuchJobError aligned with the raised type.
    sys.modules["rq.exceptions"].NoSuchJobError = no_such  # type: ignore[attr-defined]

    class _Job:
        @staticmethod
        def fetch(*_a: object, **_k: object) -> object:
            raise no_such("missing")

    sys.modules["rq.job"].Job = _Job  # type: ignore[attr-defined]

    class _Queue:
        connection = object()

    backend = object.__new__(RQJobBackend)
    backend._queue = _Queue()
    with caplog.at_level(logging.WARNING, logger="hedron.jobs.rq"):
        assert backend._fetch_rq_job("missing-id") is None
    assert not any("Job.fetch failed" in record.message for record in caplog.records)


def test_find_component_by_name_and_logical_suffix() -> None:
    from hedron_core.registry import register_component, reset_registry_for_tests, seal_registry
    from hedron_explorer.router import _find_component

    reset_registry_for_tests()
    register_component(
        logical_id="demo.Widget",
        name="Widget",
        module="tests",
        distribution="tests",
    )
    seal_registry()
    assert _find_component("Widget") is not None
    assert _find_component("missing") is None


def test_rq_fetch_unexpected_error_is_logged(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    _install_fake_rq(monkeypatch, fetch_raises=RuntimeError("redis down"))

    class _Queue:
        connection = object()

    backend = object.__new__(RQJobBackend)
    backend._queue = _Queue()
    with caplog.at_level(logging.WARNING, logger="hedron.jobs.rq"):
        assert backend._fetch_rq_job("job-1") is None
    assert any("Job.fetch failed" in record.message for record in caplog.records)
