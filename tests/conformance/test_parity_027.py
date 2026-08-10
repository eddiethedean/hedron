"""PARITY-027: Supported PAGE/FRAGMENT/CSRF semantics across hosts."""

from __future__ import annotations

import django
from django.conf import settings
from django.test import Client
from flask import Flask

from hedron import Heading, Hedron, Page, Text
from hedron.testing.adapters import (
    assert_fragment_body,
    assert_htmx_trigger,
    assert_page_document,
    django_fixture,
    fastapi_fixture,
    flask_fixture,
)
from hedron_core.htmx_contract import approved_headers
from hedron_core.interaction import (
    FragmentRegion,
    FragmentRegionError,
    InteractionPolicy,
    InteractionResult,
    authorize_oob_update,
    resolve_fragment_region,
)
from hedron_flask import HedronBlueprint, HedronFlask


def _ensure_django() -> None:
    if settings.configured:
        return
    settings.configure(
        DEBUG=True,
        SECRET_KEY="parity-027",
        ROOT_URLCONF="tests.adapters.django.urls",
        ALLOWED_HOSTS=["testserver"],
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ],
        CSRF_HEADER_NAME="HTTP_X_CSRF_TOKEN",
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


def _fastapi() -> Hedron:
    app = Hedron(
        title="parity-027",
        security="standard",
        session_secret="parity-027-secret",
        explorer="off",
    )

    @app.page("/")
    def home() -> Page:
        return Page(Heading("Parity FastAPI", level=1), title="Home")

    @app.component("/fragment")
    def fragment() -> InteractionResult:
        return InteractionResult(
            content=Text("Parity FastAPI fragment"),
            trigger="parity-refreshed",
            explanation="parity",
        )

    return app


def _flask() -> Flask:
    hedron = HedronFlask()
    ui = HedronBlueprint("ui", __name__)

    @ui.page("/")
    def home():
        return Page(Heading("Parity Flask", level=1), title="Home")

    @ui.component("/fragment")
    def fragment():
        return InteractionResult(
            content=Text("Parity Flask fragment"),
            trigger="parity-refreshed",
            explanation="parity",
        )

    app = Flask(__name__)
    app.secret_key = "parity-027"
    hedron.init_app(app)
    app.register_blueprint(ui)
    return app


def test_parity_page_document_fastapi_flask() -> None:
    for fixture, needle in (
        (fastapi_fixture(_fastapi()), "Parity FastAPI"),
        (flask_fixture(_flask()), "Parity Flask"),
    ):
        response = fixture.get("/")
        assert_page_document(response)
        assert needle in response.body


def test_parity_fragment_htmx_fastapi_flask() -> None:
    for fixture, needle in (
        (fastapi_fixture(_fastapi()), "Parity FastAPI fragment"),
        (flask_fixture(_flask()), "Parity Flask fragment"),
    ):
        response = fixture.get("/fragment", headers={"HX-Request": "true"})
        assert_fragment_body(response, contains=needle)
        assert_htmx_trigger(response, "parity-refreshed")


def test_parity_django_page_and_fragment() -> None:
    _ensure_django()
    fixture = django_fixture(Client(enforce_csrf_checks=True))
    page = fixture.get("/page/")
    assert_page_document(page)
    frag = django_fixture(Client()).get("/fragment/", headers={"HX-Request": "true"})
    assert_fragment_body(frag, contains="Fragment body")


def test_parity_shared_region_allowlist() -> None:
    policy = InteractionPolicy(declared_regions=(FragmentRegion(id="main", selector="#main"),))
    assert resolve_fragment_region(policy, "#main") is not None
    try:
        resolve_fragment_region(policy, "#other")
        raise AssertionError("expected FragmentRegionError")
    except FragmentRegionError:
        pass


def test_parity_approved_headers_reject_open_redirect() -> None:
    try:
        approved_headers(redirect="https://evil.example/")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_parity_oob_allowlist_fail_closed() -> None:
    from hedron_core import Text
    from hedron_core.interaction import OobUpdate

    regions = (FragmentRegion(id="side", selector="#side"),)
    authorize_oob_update(OobUpdate(content=Text("x"), select="#side"), regions=regions)
    try:
        authorize_oob_update(OobUpdate(content=Text("x"), select="#nope"), regions=regions)
        raise AssertionError("expected FragmentRegionError")
    except FragmentRegionError:
        pass
