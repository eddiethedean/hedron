"""Flask Blueprint / application-factory tests (phase 0.11)."""

from __future__ import annotations

from flask import Flask

from hedron_core import Heading, Page, Text
from hedron_core.interaction import InteractionResult
from hedron_flask import HedronBlueprint, HedronFlask


def create_factory_app() -> Flask:
    hedron = HedronFlask()
    ui = HedronBlueprint("ui", __name__)

    @ui.page("/")
    def home():
        return Page(Heading("Factory Home", level=1), title="Factory")

    @ui.component("/fragment")
    def fragment():
        return InteractionResult(content=Text("Blueprint fragment"), explanation="bp")

    @ui.action("/do", methods=["POST"])
    def do_action():
        return InteractionResult(content=Text("Done"), explanation="action")

    app = Flask(__name__)
    app.secret_key = "test"
    hedron.init_app(app)
    app.register_blueprint(ui)
    return app


def test_init_app_stores_extension() -> None:
    app = create_factory_app()
    assert "hedron" in app.extensions
    assert isinstance(app.extensions["hedron"], HedronFlask)


def test_blueprint_page_renders() -> None:
    client = create_factory_app().test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "Factory Home" in response.get_data(as_text=True)
    assert "<html" in response.get_data(as_text=True)


def test_blueprint_component_fragment() -> None:
    client = create_factory_app().test_client()
    response = client.get("/fragment", headers={"HX-Request": "true"})
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Blueprint fragment" in body


def test_constructor_compat_still_works() -> None:
    hedron = HedronFlask(__name__)
    assert hedron.flask is not None
    assert hedron.flask.extensions["hedron"] is hedron


def test_csrf_cookie_seeded_on_get() -> None:
    client = create_factory_app().test_client()
    response = client.get("/")
    assert "hedron_csrf" in response.headers.get("Set-Cookie", "")


def test_action_requires_csrf() -> None:
    client = create_factory_app().test_client()
    response = client.post("/do")
    assert response.status_code == 403


def test_include_component_csrf_on_unsafe_methods() -> None:
    from hedron_core import addressable
    from hedron_core.registry import reset_registry_for_tests

    reset_registry_for_tests()

    @addressable(methods=("GET", "POST"))
    def piece():
        return Text("piece")

    hedron = HedronFlask()
    ui = HedronBlueprint("ui_inc", __name__)
    ui.include_component(piece, path="/piece", methods=["GET", "POST"])
    app = Flask(__name__)
    app.secret_key = "test"
    hedron.init_app(app)
    app.register_blueprint(ui)
    client = app.test_client()

    assert client.get("/piece").status_code == 200
    assert client.post("/piece").status_code == 403

    seeded = client.get("/piece")
    set_cookie = seeded.headers.get("Set-Cookie", "")
    assert "hedron_csrf=" in set_cookie
    cookie = set_cookie.split("hedron_csrf=")[1].split(";")[0]
    ok = client.post(
        "/piece",
        headers={"X-CSRF-Token": cookie},
        data={"csrf_token": cookie},
    )
    assert ok.status_code == 200


def test_hedron_flask_page_component_action() -> None:
    hedron = HedronFlask(__name__)
    assert hedron.flask is not None
    hedron.flask.secret_key = "test"

    @hedron.page("/p")
    def page_view():
        return Page(Heading("App Page", level=1), title="P")

    @hedron.component("/c")
    def component_view():
        return Text("comp")

    client = hedron.flask.test_client()
    assert "App Page" in client.get("/p").get_data(as_text=True)
    assert "comp" in client.get("/c").get_data(as_text=True)
