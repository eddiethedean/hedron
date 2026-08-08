"""REGION-020: Flask/Django fragment_regions merge for InteractionResult returns."""

from __future__ import annotations

import django
import pytest
from django.conf import settings
from flask import Flask

from hedron_core import Page, Text
from hedron_core.interaction import FragmentRegion, InteractionResult
from hedron_flask import HedronBlueprint, HedronFlask

PANEL = FragmentRegion(id="panel", selector="#panel")


@pytest.fixture(scope="module")
def _django_ready() -> None:
    if settings.configured:
        return
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-secret",
        ROOT_URLCONF="tests.adapters.django.urls",
        ALLOWED_HOSTS=["testserver"],
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "hedron_django.middleware.HedronSecurityHeadersMiddleware",
        ],
        HEDRON_SECURITY_PROFILE="standard",
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django.contrib.sessions",
            "hedron_django.apps.HedronDjangoConfig",
        ],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        USE_TZ=True,
    )
    django.setup()


def _flask_app(*, declare: bool) -> Flask:
    hedron = HedronFlask()
    ui = HedronBlueprint("ui_regions", __name__)
    regions = (PANEL,) if declare else None

    @ui.component("/fragment", fragment_regions=regions)
    def fragment():
        # Handler omits policy.declared_regions — route allowlist must still authorize.
        return InteractionResult(content=Text("panel body"), explanation="region demo")

    app = Flask(__name__)
    app.secret_key = "test"
    hedron.init_app(app)
    app.register_blueprint(ui)
    return app


def test_flask_action_declared_fragment_regions_allow_hx_target() -> None:
    hedron = HedronFlask()
    ui = HedronBlueprint("ui_action_ok", __name__)

    @ui.page("/")
    def home():
        return Page(Text("home"), title="Home")

    @ui.action("/save", fragment_regions=(PANEL,))
    def save():
        return Text("saved")

    app = Flask(__name__)
    app.secret_key = "test"
    hedron.init_app(app)
    app.register_blueprint(ui)
    client = app.test_client()
    seeded = client.get("/")
    set_cookie = seeded.headers.get("Set-Cookie", "")
    assert "hedron_csrf=" in set_cookie
    token = set_cookie.split("hedron_csrf=")[1].split(";")[0]
    response = client.post(
        "/save",
        headers={
            "HX-Request": "true",
            "HX-Target": "#panel",
            "X-CSRF-Token": token,
        },
    )
    assert response.status_code == 200
    assert "saved" in response.get_data(as_text=True)


def test_flask_action_undeclared_hx_target_is_forbidden() -> None:
    hedron = HedronFlask()
    ui = HedronBlueprint("ui_action_deny", __name__)

    @ui.page("/")
    def home():
        return Page(Text("home"), title="Home")

    @ui.action("/save")
    def save():
        return Text("saved")

    app = Flask(__name__)
    app.secret_key = "test"
    hedron.init_app(app)
    app.register_blueprint(ui)
    client = app.test_client()
    seeded = client.get("/")
    token = seeded.headers.get("Set-Cookie", "").split("hedron_csrf=")[1].split(";")[0]
    response = client.post(
        "/save",
        headers={
            "HX-Request": "true",
            "HX-Target": "#panel",
            "X-CSRF-Token": token,
        },
    )
    assert response.status_code == 403


def test_flask_declared_fragment_regions_allow_hx_target() -> None:
    client = _flask_app(declare=True).test_client()
    response = client.get(
        "/fragment",
        headers={"HX-Request": "true", "HX-Target": "#panel"},
    )
    assert response.status_code == 200
    assert "panel body" in response.get_data(as_text=True)


def test_flask_undeclared_hx_target_is_forbidden() -> None:
    client = _flask_app(declare=False).test_client()
    response = client.get(
        "/fragment",
        headers={"HX-Request": "true", "HX-Target": "#panel"},
    )
    assert response.status_code == 403


def test_flask_declared_regions_reject_unauthorized_target() -> None:
    client = _flask_app(declare=True).test_client()
    response = client.get(
        "/fragment",
        headers={"HX-Request": "true", "HX-Target": "#evil"},
    )
    assert response.status_code == 403


def test_django_declared_fragment_regions_allow_hx_target(_django_ready: None) -> None:
    from django.http import HttpRequest
    from django.test import RequestFactory

    from hedron_django import hedron_view

    @hedron_view(fragment_regions=(PANEL,))
    def fragment(request: HttpRequest):
        return InteractionResult(content=Text("django panel"), explanation="dj")

    request = RequestFactory().get(
        "/region-fragment/",
        HTTP_HX_REQUEST="true",
        HTTP_HX_TARGET="#panel",
    )
    response = fragment(request)
    assert response.status_code == 200
    assert b"django panel" in response.content


def test_django_undeclared_hx_target_is_forbidden(_django_ready: None) -> None:
    from django.http import HttpRequest
    from django.test import RequestFactory

    from hedron_django import hedron_view

    @hedron_view
    def fragment(request: HttpRequest):
        return InteractionResult(content=Text("django panel"), explanation="dj")

    request = RequestFactory().get(
        "/region-fragment-open/",
        HTTP_HX_REQUEST="true",
        HTTP_HX_TARGET="#panel",
    )
    response = fragment(request)
    assert response.status_code == 403


def test_django_declared_regions_reject_unauthorized_target(_django_ready: None) -> None:
    from django.http import HttpRequest
    from django.test import RequestFactory

    from hedron_django import hedron_view

    @hedron_view(fragment_regions=(PANEL,))
    def fragment(request: HttpRequest):
        return InteractionResult(content=Text("django panel"), explanation="dj")

    request = RequestFactory().get(
        "/region-fragment/",
        HTTP_HX_REQUEST="true",
        HTTP_HX_TARGET="#evil",
    )
    response = fragment(request)
    assert response.status_code == 403
