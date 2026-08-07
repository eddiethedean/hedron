"""AUTH-020: Flask-Login current_user preferred for HedronFlask.auth_signal."""

from __future__ import annotations

import sys
import types
from typing import Any

from flask import session

from hedron_core import Text
from hedron_core.interaction import InteractionResult
from hedron_flask import HedronFlask
from hedron_flask.responses import interaction_response


def _install_fake_flask_login(monkeypatch: Any, *, authenticated: bool, user_id: str) -> None:
    class _User:
        is_authenticated = authenticated

        def get_id(self) -> str | None:
            return user_id if authenticated else None

    fake = types.ModuleType("flask_login")
    fake.current_user = _User()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "flask_login", fake)


def test_auth_signal_without_flask_login_uses_session_user_id() -> None:
    """Session fallback when flask_login is not installed / not authenticated."""
    hedron = HedronFlask(__name__)
    app = hedron.flask
    assert app is not None
    app.secret_key = "test"
    with app.test_request_context("/"):
        session["user_id"] = "session-user"
        signal = hedron.auth_signal()
    assert signal.authenticated is True
    assert signal.subject_id == "session-user"


def test_auth_signal_without_flask_login_uses_underscore_user_id() -> None:
    hedron = HedronFlask(__name__)
    app = hedron.flask
    assert app is not None
    app.secret_key = "test"
    with app.test_request_context("/"):
        session["_user_id"] = "legacy-user"
        signal = hedron.auth_signal()
    assert signal.authenticated is True
    assert signal.subject_id == "legacy-user"


def test_auth_signal_prefers_flask_login_current_user(monkeypatch: Any) -> None:
    _install_fake_flask_login(monkeypatch, authenticated=True, user_id="fl-user")
    hedron = HedronFlask(__name__)
    app = hedron.flask
    assert app is not None
    app.secret_key = "test"
    with app.test_request_context("/"):
        session["user_id"] = "session-user"
        signal = hedron.auth_signal()
    assert signal.authenticated is True
    assert signal.subject_id == "fl-user"


def test_auth_signal_falls_back_when_flask_login_anonymous(monkeypatch: Any) -> None:
    _install_fake_flask_login(monkeypatch, authenticated=False, user_id="ignored")
    hedron = HedronFlask(__name__)
    app = hedron.flask
    assert app is not None
    app.secret_key = "test"
    with app.test_request_context("/"):
        session["user_id"] = "session-user"
        signal = hedron.auth_signal()
    assert signal.authenticated is True
    assert signal.subject_id == "session-user"


def test_authenticated_signal_sets_private_cache(monkeypatch: Any) -> None:
    _install_fake_flask_login(monkeypatch, authenticated=True, user_id="fl-user")
    hedron = HedronFlask(__name__)
    app = hedron.flask
    assert app is not None
    app.secret_key = "test"
    with app.test_request_context("/"):
        signal = hedron.auth_signal()
        assert signal.authenticated is True
        response = interaction_response(
            InteractionResult(content=Text("secret"), explanation="auth"),
            authenticated=signal.authenticated,
        )
    assert "private" in (response.headers.get("Cache-Control") or "")
    assert "no-store" in (response.headers.get("Cache-Control") or "")
