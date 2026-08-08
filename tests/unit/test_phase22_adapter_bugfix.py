"""Adapter regressions for 0.22 CSRF / headers bugfix dive."""

from __future__ import annotations

import pytest
from flask import Flask

from hedron_core.builtins.forms import CsrfField
from hedron_core.csrf_strategy import SessionTokenCsrf
from hedron_core.security_policy import SecurityHeadersPolicy, SecurityPolicy
from hedron_flask import HedronFlask


def test_flask_csrf_disabled_skips_cookie() -> None:
    policy = SecurityPolicy(csrf_enabled=False, security_headers=False)
    hedron = HedronFlask(
        __name__,
        security=policy,
        csrf_protect=False,
        auto_csrf_cookie=True,
    )

    @hedron.page("/")
    def home():
        from hedron_core.builtins.content import Text
        from hedron_core.builtins.document import Page

        return Page(Text("ok"), title="home")

    client = hedron.flask.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "hedron_csrf" not in (response.headers.get("Set-Cookie") or "")


def test_flask_rejects_session_token_strategy() -> None:
    policy = SecurityPolicy(csrf=SessionTokenCsrf(get_expected=lambda _r: "x"))
    with pytest.raises(ValueError, match="DoubleSubmitCookieCsrf"):
        HedronFlask(__name__, security=policy)


def test_flask_render_context_supplies_csrf_field() -> None:
    hedron = HedronFlask(__name__, security="standard")

    @hedron.page("/")
    def home():
        from hedron_core.builtins.content import Text
        from hedron_core.builtins.document import Page

        return Page(CsrfField(), Text("form"), title="home")

    client = hedron.flask.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert 'name="csrf_token"' in response.get_data(as_text=True)
    assert 'type="hidden"' in response.get_data(as_text=True)


def test_flask_cookie_path_uses_script_root() -> None:
    from hedron_flask.csrf import ensure_csrf_cookie

    app = Flask(__name__)
    hedron = HedronFlask(security="standard")
    hedron.init_app(app)

    @app.route("/")
    def index():
        from flask import make_response, request

        resp = make_response("ok")
        token = hedron.csrf_token(request)
        ensure_csrf_cookie(resp, token, path="/mount")
        return resp

    client = app.test_client()
    response = client.get("/")
    assert "Path=/mount" in (response.headers.get("Set-Cookie") or "")


def test_django_security_headers_policy_from_settings() -> None:
    pytest.importorskip("django")
    from hedron_django.middleware import security_policy_from_settings

    class _Settings:
        HEDRON_SECURITY_PROFILE = "standard"
        HEDRON_SECURITY_HEADERS = SecurityHeadersPolicy(
            content_security_policy="default-src 'none'"
        )

    policy = security_policy_from_settings(_Settings())
    headers = policy.response_headers()
    assert headers["Content-Security-Policy"] == "default-src 'none'"
    assert headers["X-Frame-Options"] == "DENY"
