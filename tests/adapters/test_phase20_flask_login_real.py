"""AUTH-020: real Flask-Login session → HedronFlask.auth_signal (not a sys.modules stub)."""

from __future__ import annotations

import pytest

flask_login = pytest.importorskip("flask_login")

from flask import Flask  # noqa: E402
from flask_login import LoginManager, UserMixin, login_user  # noqa: E402

from hedron_core import Text  # noqa: E402
from hedron_core.interaction import InteractionResult  # noqa: E402
from hedron_flask import HedronFlask  # noqa: E402
from hedron_flask.responses import interaction_response  # noqa: E402


class _User(UserMixin):
    def __init__(self, user_id: str) -> None:
        self.id = user_id

    def get_id(self) -> str:
        return self.id


def _app_with_login() -> tuple[HedronFlask, Flask, LoginManager]:
    hedron = HedronFlask(__name__)
    app = hedron.flask
    assert app is not None
    app.secret_key = "test-secret"
    login_manager = LoginManager()
    login_manager.init_app(app)
    users = {"fl-user": _User("fl-user")}

    @login_manager.user_loader
    def load_user(user_id: str) -> _User | None:
        return users.get(user_id)

    return hedron, app, login_manager


def test_auth_signal_uses_real_flask_login_session() -> None:
    hedron, app, _login_manager = _app_with_login()
    with app.test_request_context("/"):
        assert login_user(_User("fl-user")) is True
        signal = hedron.auth_signal()
    assert signal.authenticated is True
    assert signal.subject_id == "fl-user"


def test_real_flask_login_preferred_over_session_user_id() -> None:
    hedron, app, _login_manager = _app_with_login()
    with app.test_request_context("/"):
        from flask import session

        session["user_id"] = "session-user"
        assert login_user(_User("fl-user")) is True
        signal = hedron.auth_signal()
    assert signal.authenticated is True
    assert signal.subject_id == "fl-user"


def test_real_flask_login_sets_private_cache_on_interaction() -> None:
    hedron, app, _login_manager = _app_with_login()
    with app.test_request_context("/"):
        assert login_user(_User("fl-user")) is True
        signal = hedron.auth_signal()
        assert signal.authenticated is True
        response = interaction_response(
            InteractionResult(content=Text("secret"), explanation="auth"),
            authenticated=signal.authenticated,
        )
    assert "private" in (response.headers.get("Cache-Control") or "")
    assert "no-store" in (response.headers.get("Cache-Control") or "")
